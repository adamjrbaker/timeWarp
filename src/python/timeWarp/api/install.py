"""Install setup for timeWarp"""

# Python
import os
import glob
import shutil

# Maya
import maya.mel
import maya.cmds

MOD_INPUT_TEXT = "+ timeWarp x.x PATH/timeWarp\n"\
                 "scripts: ./src/python/api\n"\
                 "icons: ./src/python/icons"

TIMEWARP_MOD = "timeWarp.mod"


ICON_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../', 'icons')


def install(module_path, script_path, version):
    """ Install files based on location set in GUI

    Args:
        module_path (str): Path to where modules should be saved.
        script_path (str): Path to where scripts should be saved.
        version (str): Version number.

    Returns:
        None
    """
    build_mod_file(module_path, script_path, version)
    plugin_path = transfer_scripts(script_path)
    load_plugin(plugin_path)


def get_script_path():
    """ Get Maya's scripts path at root level.

    Returns:
        str to path of modules.
    """

    return os.path.abspath(os.path.join(maya.mel.eval("internalVar -upd"), "../../scripts"))


def get_module_path():
    """ Get Maya's modules path at root level.

    Returns:
        str to path of modules.
    """

    return os.path.abspath(os.path.join(maya.mel.eval("internalVar -upd"), "../../modules"))


def installed_mod_path():
    """ Get installed module path if found.

    Returns:
        str of path to timeWarp.mod
    """
    for path in os.getenv("MAYA_MODULE_PATH").split(":"):
        if glob.glob(os.path.join(path, TIMEWARP_MOD)):
            return path


def build_mod_file(module_path, scripts_path, version):
    """ Build moc file and copy it to correct location.

    Args:
        module_path (str): Module path location.
        scripts_path (str): Scripts path location.
        version (str): Version number.

    Returns:
        if successful return str of path to mod file.
    """

    mod_text = MOD_INPUT_TEXT.replace("PATH", scripts_path)
    mod_text = mod_text.replace("x.x", version)

    # Check if "maya/modules" folder already exists
    module_file_path = os.path.join(module_path, TIMEWARP_MOD)
    os.environ['MAYA_PLUG_IN_PATH'] += ":{}".format(module_file_path)
    if not os.path.isdir(module_path):
        try:
            os.mkdir(module_path)
        # In the case we can't make the folder we need to fail out.
        except:
            return False

    if os.path.isfile(module_file_path) and TIMEWARP_MOD in module_file_path:
        try:
            os.remove(module_file_path)
        # Make sure we can delete the file else we need to fail out.
        except:
            return False

    # Now we can write out the file.
    with open(module_file_path, "w") as fileInstance:
        fileInstance.write(mod_text)

    return module_file_path


def transfer_scripts(scripts_path):
    """ Transfer files to scripts location.

    Args:
        scripts_path (str): Path to scripts location.

    Returns:
        string: of plugin path.
    """

    destination_path = os.path.join(scripts_path, 'timeWarp')

    if os.path.isdir(destination_path):
        try:
            shutil.rmtree(destination_path)
        # Make sure we can delete the file else we need to fail out.
        except:
            return

    # Make path to copy files to.
    os.mkdir(destination_path)

    source = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../timeWarp')

    copy_files(source, destination_path)

    plugin_path = os.path.join(source, 'plug-ins')

    return plugin_path


def load_plugin(plugin_path):
    """ Load plugin file.

    Args:
        plugin_path (str): Path to file directory.

    Returns:
        None
    """
    os.environ['MAYA_MODULE_PATH'] += ":{}".format(plugin_path)
    os.environ['MAYA_PLUG_IN_PATH'] += ":{}".format(plugin_path)

    plugin_py_path = os.path.join(plugin_path, 'WarpStatus.py')

    maya.cmds.loadPlugin(plugin_py_path, quiet=True)
    maya.cmds.pluginInfo(plugin_py_path, edit=True, autoload=True)


def copy_files(source_folder, destination_folder):
    """ Copy tree from one location to another.

    Args:
        source_folder (str): Source file location.
        destination_folder (str): Destination location to copy files

    Returns:
        None
    """
    # Create the destination folder if it doesn't exist
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # Iterate through all the files and subdirectories in the source folder
    for root, dirs, files in os.walk(source_folder):

        if '.git' in dirs:
            dirs.remove('.git')

        # Create the corresponding subdirectory structure in the destination folder
        relative_path = os.path.relpath(root, source_folder)
        destination_path = os.path.join(destination_folder, relative_path)
        if not os.path.exists(destination_path):
            os.makedirs(destination_path)

        # Copy files from the source folder to the destination folder
        for file in files:
            source_file = os.path.join(root, file)
            destination_file = os.path.join(destination_path, file)
            shutil.copy2(source_file, destination_file)


def create_shelf_button(force=False):
    """ Create shelf button to launch GUI.

    Args:
        force (bool | False): If button should be made with force..

    Returns:
        bool if shelf button is created.
    """

    icon = os.path.join(ICON_PATH, "TimeWarpShelf.svg")

    command = 'from timeWarp.api import widget; widget.launch()'

    # Get all the children buttons of the shelf layout
    shelf_buttons = maya.cmds.shelfLayout(maya.cmds.shelfLayout('Custom', query=True, fullPathName=True),
                                          query=True, childArray=True) or []

    # Check if any button matches the label
    button_exists = any(maya.cmds.shelfButton(button, query=True, label=True) == 'Launch Time Warp GUI'
                        for button in shelf_buttons)

    if not button_exists or force:
        maya.cmds.shelfButton(label='Launch Time Warp GUI', parent='Custom', command=command, image=icon,
                              imageOverlayLabel="", annotation='Launch Time Warp GUI',
                              noDefaultPopup=True, sourceType='python')

        maya.cmds.shelfTabLayout('ShelfLayout', edit=True, selectTab='Custom')

        return True

    return False
