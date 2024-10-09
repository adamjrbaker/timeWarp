""" Maya Test Base"""

# python
import atexit
import unittest
import os
import sys
import shutil
import tempfile

# Add repository base path to system paths, so Maya can access atk.
tests_path = os.path.dirname(os.path.realpath(__file__))
base_path = os.path.join(tests_path.rsplit(os.sep, 2)[0], 'api', 'python')
if base_path not in sys.path:
    sys.path.insert(0, base_path)

# Initialize Maya - otherwise tests run before Maya is actually ready!
import maya.standalone
maya.standalone.initialize()
import maya.cmds


class TestMayaBase(unittest.TestCase):
    """ Maya Test Base Class"""

    def setup(self):
        """ Setup new maya scene.

        Returns:
            None
        """
        super(TestMayaBase, self).setup()
        maya.cmds.file(newFile=True, force=True)

    @staticmethod
    def save_scene(path, file_type="mayaAscii"):
        """ Save maya scene file at a given path.

        Args:
            path (str): Path to maya scene file including extension
            file_type (str | file_type): Name of maya file type
        Returns:
            Return path to scene.
        """
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, force=True, type=file_type)
        return path

    @staticmethod
    def open_scene(path):
        """ Open maya scene from a given path.

        Args:
            path (str): path to maya scene file including extension

        Returns:
            None
        """
        maya.cmds.file(path, open=True, force=True)

    @staticmethod
    def new_scene():
        """ Create new scene.

        Returns:
            None
        """
        maya.cmds.file(new=True, force=True)

    def create_workspace(self):
        """ Create temp maya workspace.

        Returns:
            string of temp path.
        """
        self.temp_dir = tempfile.mkdtemp()

        project_path = maya.cmds.workspace(self.temp_dir, openWorkspace=True)

        return self.temp_dir

    def cleanup_workspace(self):
        """ Clean up maya temp workspace.

        Returns:
            None
        """

        shutil.rmtree(self.temp_dir)

    @staticmethod
    def assert_xform_match(node_one, node_two, translate=False, rotate=False, scale=False):
        """ Check xfrom match on two give maya nodes. Because of maya's precision issues we round the xfrom matrix to
        10 decimal points.

        Args:
            node_one (str): Maya Node
            node_two (str): Maya Node
            translate (bool | False): Check for translation match.
            rotate (bool | False): Check for rotation match.
            scale (bool | False): Check for scale match.

        Returns:
            Bool if nodes match.
        """

        result = False

        if translate:
            node_one_trans = [round(num, 10) for num in maya.cmds.xform(node_one, translation=True, query=True)]
            node_two_trans = [round(num, 10) for num in maya.cmds.xform(node_two, translation=True, query=True)]
            if node_one_trans == node_two_trans:
                result = True
        if rotate:
            node_one_rot = [round(num, 10) for num in maya.cmds.xform(node_one, rotation=True, query=True)]
            node_two_rot = [round(num, 10) for num in maya.cmds.xform(node_two, rotation=True, query=True)]
            if node_one_rot == node_two_rot:
                result = True
        if scale:
            node_one_scale = [round(num, 10) for num in maya.cmds.xform(node_one, scale=True,
                                                                        query=True, relative=True)]
            node_two_scale = [round(num, 10) for num in maya.cmds.xform(node_two, scale=True,
                                                                        query=True, relative=True)]
            if node_one_scale == node_two_scale:
                result = True

        return result
