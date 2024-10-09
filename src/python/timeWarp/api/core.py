""" Time Warp Core """

# Python
import re

# Maya
import maya.cmds
import maya.mel

from timeWarp._versions import __version__, __doc__, __author__, __email__, __copyright__

# Maya's main progress bar
MAIN_PROGRESS_BAR = maya.mel.eval('$tmp = $gMainProgressBar')


def create_warp(warp_name=None, anti_warp=False):
    """ Create warp nodes.

    Args:
        warp_name (str | None): Custom name of time warp curve.
        anti_warp (bool | False): If warp node should be a anti warp.

    Returns:
        maya node name of warp time curve.
    """

    min_time = maya.cmds.playbackOptions(query=True, minTime=True)
    max_time = maya.cmds.playbackOptions(query=True, maxTime=True)

    curve_name = 'atk_WarpCurve'
    connection_name = "atk_warpSettings"

    if warp_name:
        curve_name = warp_name
        connection_name = '{}_warpSettings'.format(warp_name)

    if anti_warp:
        curve_name = '{}_AntiWarp'.format(curve_name)

    warp_node = maya.cmds.createNode('animCurveTT', name=curve_name)
    maya.cmds.setAttr(warp_node + ".preInfinity", 1)
    maya.cmds.setAttr(warp_node + ".postInfinity", 1)

    # Anti warp is created based on the scene time warp
    if anti_warp:
        for frame in range(min_time, max_time + 1):
            time = maya.cmds.getAttr('time1.outTime', time=frame)
            maya.cmds.setKeyframe(warp_node, time=time, value=frame)
    else:
        maya.cmds.setKeyframe(warp_node, time=min_time, value=min_time, inTangentType="spline", outTangentType="spline")
        maya.cmds.setKeyframe(warp_node, time=max_time, value=max_time, inTangentType="spline", outTangentType="spline")

    status_node = maya.cmds.createNode('WarpStatus', name=re.sub(curve_name, warp_node, connection_name))

    # Set connections for toggle node
    maya.cmds.connectAttr(warp_node + ".output", status_node + ".warpInput", force=True)
    # Connect real time to the alternate condition
    maya.cmds.connectAttr("time1.outTime", status_node + ".timeInput", force=True)

    return status_node


def apply_warp(warp_node):
    """ Apply Warp to selected nodes.

    Args:
        warp_node (str): Name of warp node to apply the on the selected objects

    Returns:
        Bool If applied
    """

    selection = maya.cmds.ls(selection=True, dag=True, long=True)

    if not selection:
        return False

    input_nodes = []

    with ProgressBarContextManager(len(selection), message="Getting Input Nodes.") as progress_bar:
        for node in selection:
            input_nodes = list(set(input_nodes + get_inputs(node)))
            progress_bar.update_progress()

    if not input_nodes:
        return False

    with ProgressBarContextManager(len(input_nodes), message="Adding Input Nodes.") as progress_bar:
        maya.cmds.undoInfo(openChunk=True, stateWithoutFlush=True)
        for connection in input_nodes:
            node_type = maya.cmds.nodeType(connection)

            if node_type in ["animCurveTU", "animCurveTA", "animCurveTL"]:
                maya.cmds.connectAttr("{}.output".format(warp_node), '{}.input'.format(connection), force=True)

            progress_bar.update_progress()

        maya.cmds.undoInfo(closeChunk=True, stateWithoutFlush=True)

    return True


def remove_warp(warp_node):
    """ Remove Warp to selected nodes.

    Args:
        warp_node (str): Name of warp node to remove the on the selected objects

    Returns:
        Bool If removed
    """

    selection = maya.cmds.ls(selection=True, dag=True, long=True)

    if not selection:
        return False

    input_nodes = []

    with ProgressBarContextManager(len(selection), message="Getting Input Nodes.") as progress_bar:
        for node in selection:
            input_nodes = list(set(input_nodes + get_inputs(node)))
            progress_bar.update_progress()

    if not input_nodes:
        return False

    with ProgressBarContextManager(len(input_nodes), message="Removing Input Nodes.") as progress_bar:
        maya.cmds.undoInfo(openChunk=True, stateWithoutFlush=True)
        for connection in input_nodes:
            node_type = maya.cmds.nodeType(connection)

            if node_type in ["animCurveTU", "animCurveTA", "animCurveTL"]:
                try:
                    maya.cmds.disconnectAttr("{}.output".format(warp_node), '{}.input'.format(connection))
                except RuntimeError:
                    continue
            progress_bar.update_progress()
        maya.cmds.undoInfo(closeChunk=True, stateWithoutFlush=True)

    return True


def delete_warp(warp_node):
    """

    Args:
        warp_node (str): Name of warp node to delete

    Returns:
        None
    """

    maya.cmds.delete(warp_node)


def get_inputs(node):
    """ Get input nodes of selected node.

    Args:
        node (str): Name of maya node to check.

    Returns:
        List of connections of that node.
    """

    results = []

    # Get geo nodes connections.
    geo_inputs = maya.cmds.listConnections(node, source=True, destination=False,
                                           skipConversionNodes=True, type="geometryFilter") or []
    # Get connected animation curves.
    anim_curves = maya.cmds.listConnections(node, source=True, destination=False,
                                            skipConversionNodes=True, type="animCurve") or []
    # Make sure we aren't having any duplicates.
    inputs = list(set(geo_inputs + anim_curves))

    if not inputs:
        return results

    # We can make sure we have no connections of connections.
    for connection in inputs:
        results += get_inputs(connection)

    return list(set(inputs + results))


def get_warp_nodes():
    """ Get all warp nodes in scene.

    Returns:
        list of warp nodes
    """

    return maya.cmds.ls(type="WarpStatus")


def get_warped_nodes(warp):
    """Get all warped nodes for warp

    Args:
        warp (str): Maya warp node.

    Returns:
        list of nodes effected by warp.
    """

    warped = []

    curves = maya.cmds.listConnections(warp, source=False, destination=True, skipConversionNodes=True)

    if not curves:
        return warped

    for curve in curves:
        nodes = maya.cmds.listConnections(curve, source=False, destination=True, skipConversionNodes=True)
        for node in nodes:
            if node not in warped:
                warped.append(node)

    return warped


def select_warped_nodes(warp):
    """ Select warped nodes.

    Args:
        warp (str): Maya warp node.

    Returns:
        None
    """

    warped_nodes = get_warped_nodes(warp)

    if warped_nodes:
        maya.cmds.select(warped_nodes, replace=True)
    else:
        maya.cmds.select(clear=True)


def get_warp_curve(warp):
    """ Get curve of warp.

    Args:
        warp (str): Maya warp node.

    Returns:
        str of warp curve name.
    """

    # We need to get the input of warpInput and get that nodes parent.
    warp_curve = maya.cmds.listConnections(maya.cmds.listConnections("{}.wi" .format(warp),
                                                                     source=True, destination=False),
                                           source=True, destination=False)

    return warp_curve


def select_warp_curve(warp):
    """ Select warped curve node.

    Args:
        warp (str): Maya warp node.

    Returns:
        None
    """

    warp_curve = get_warp_curve(warp)

    if warp_curve:
        maya.cmds.select(warp_curve, replace=True)
    else:
        maya.cmds.select(clear=True)


def bake_warp(warp, steps=1):
    """ Bake out warp and delete.

    Args:
        warp (str): Maya warp node.
        steps (int | 1): How often to bake.

    Returns:
        True if baked out.
    """

    warped_nodes = get_warped_nodes(warp)

    if warped_nodes:

        frame_start = maya.cmds.playbackOptions(query=True, minTime=True, animationStartTime=False)
        frame_end = maya.cmds.playbackOptions(query=True, maxTime=True, animationEndTime=False)

        maya.cmds.bakeResults(warped_nodes, sampleBy=steps, time=(frame_start, frame_end),
                              simulation=True, preserveOutsideKeys=True)

        return True

    return False


def is_warp_active(warp):
    """ Check if the warp is active

    Args:
        warp (str): Maya warp node.

    Returns:
        Bool if active
    """

    return maya.cmds.getAttr('{}.warpActive' .format(warp))


def set_warp_status(warp, status):
    """ set warp status.

    Args:
        warp (str): Maya warp node.
        status (bool): If warp should be active.

    Returns:
        None
    """

    maya.cmds.setAttr('{}.warpActive' .format(warp), status)


class ProgressBarContextManager:
    """Context manager to make using the main progress bar easy."""
    def __init__(self, total_steps, title='Time Warp', message='Processing Time Warp...'):
        """ Create context manager

        Args:
            total_steps (int): Number of steps in process.
            title (str | Time Warp): Name of progress in progress bar.
            message (str | Progress Time Warp...): Name of message of progress.
        """
        self.total_steps = total_steps
        self.title = title
        self.message = message

    def __enter__(self):
        """ ContextManager Enter.

        Returns:
            self
        """
        maya.cmds.progressBar(MAIN_PROGRESS_BAR,
                              edit=True,
                              beginProgress=True,
                              isInterruptable=True,
                              status='"Example Calculation ...',
                              maxValue=self.total_steps)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ On exit of contextManger.

        Returns:
            None
        """
        maya.cmds.progressBar(MAIN_PROGRESS_BAR, edit=True, endProgress=True)

    def update_progress(self):
        """ Update progress by 1.

        Returns:
            None
        """
        maya.cmds.progressBar(MAIN_PROGRESS_BAR, edit=True, step=1, status=self.message)
