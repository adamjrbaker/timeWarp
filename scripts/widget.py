""" Time Warp Widget"""

# Python
import os

# Qt
from PySide2 import QtCore, QtWidgets, QtGui

from timeWarp.scripts import core
ICON_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../', 'icons')

_WIDGET = None


class TimeWarp(QtWidgets.QDialog):
    """ Time Warp Widget"""

    def __init__(self):
        super(TimeWarp, self).__init__()

        # Build UI
        self.setWindowTitle('Time Warp')
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowIcon(QtGui.QIcon(os.path.join(ICON_PATH, 'WarpStatus.png')))

        self.setGeometry(300, 300, 300, 350)
        self.setMinimumSize(400, 350)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(main_layout)

        select_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(select_layout)

        self.create_warp_btn = QtWidgets.QPushButton("Create")
        self.create_warp_btn.setFixedWidth(70)
        self.create_warp_btn.setFixedHeight(30)
        self.create_warp_btn.setStyleSheet("background-color : #16A085")
        self.create_warp_btn.clicked.connect(self.create_warp)
        select_layout.addWidget(self.create_warp_btn)

        self.warp_select = QtWidgets.QComboBox()
        self.warp_select.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.warp_select.setFixedHeight(30)
        self.warp_select.setMinimumWidth(170)
        self.warp_select.currentTextChanged.connect(self.on_select_change)
        select_layout.addWidget(self.warp_select)

        self.active = QtWidgets.QCheckBox("Warp Active")
        self.active.toggled.connect(self.set_active_status)
        select_layout.addWidget(self.active)

        self.select_warp_btn = QtWidgets.QPushButton("Select Warp")
        self.select_warp_btn.setFixedHeight(45)
        self.select_warp_btn.clicked.connect(lambda: core.select_warp_curve(self.warp_select.currentText()))
        main_layout.addWidget(self.select_warp_btn)

        self.select_warped_btn = QtWidgets.QPushButton("Select Warped")
        self.select_warped_btn.setFixedHeight(45)
        self.select_warped_btn.clicked.connect(lambda: core.select_warped_nodes(self.warp_select.currentText()))
        main_layout.addWidget(self.select_warped_btn)

        self.add_btn = QtWidgets.QPushButton("Add To Warp")
        self.add_btn.setFixedHeight(45)
        self.add_btn.clicked.connect(self.on_add)
        main_layout.addWidget(self.add_btn)

        self.remove_btn = QtWidgets.QPushButton("Remove From Warp")
        self.remove_btn.setFixedHeight(45)
        self.remove_btn.clicked.connect(self.on_remove)
        main_layout.addWidget(self.remove_btn)

        self.bake_btn = QtWidgets.QPushButton("Bake Out Warp")
        self.bake_btn.setFixedHeight(45)
        self.bake_btn.clicked.connect(self.on_bake)
        main_layout.addWidget(self.bake_btn)

        self.delete_btn = QtWidgets.QPushButton("Delete Warp")
        self.delete_btn.setStyleSheet("background-color : #E74C3C")
        self.delete_btn.clicked.connect(self.on_delete)
        main_layout.addWidget(self.delete_btn)

        # add scene data to widgets.
        self.add_scene_data()

    def add_scene_data(self):
        """ Run this after building of GUI to set the widget based on scene.

        Returns:
            None
        """

        self.warp_select.blockSignals(True)
        self.active.blockSignals(True)

        # Add Scene warps to widget.
        self.warp_select.addItems(core.get_warp_nodes())

        # set warp status of current warp.
        current_warp = self.warp_select.currentText()

        if current_warp:
            status = core.is_warp_active(current_warp)
            self.active.setChecked(status)

        self.warp_select.blockSignals(False)
        self.active.blockSignals(False)

    def create_warp(self):
        """ Create warp and add to select.

        Returns:
            None
        """

        warp_name, create = QtWidgets.QInputDialog.getText(self, "Time Warp", "Warp Name:",
                                                           QtWidgets.QLineEdit.Normal, "atk")

        if warp_name and create:
            name = core.create_warp(warp_name=warp_name)
            self.warp_select.addItem(name)
            self.warp_select.setCurrentText(name)

    def set_active_status(self, status):
        """ Change active status of warp.

        Args:
            status (bool): Current state of checkbox.

        Returns:
            None
        """

        current_warp = self.warp_select.currentText()
        core.set_warp_status(current_warp, status)

    def on_select_change(self, current_warp):
        """ On change of warp select.

        Args:
            current_warp (str): Name of Current warp.

        Returns:
            None
        """

        status = core.is_warp_active(current_warp)
        self.active.setChecked(status)

    def on_add(self):
        """ On adding objects to warp check for selection.

        Returns:
            None
        """

        status = core.apply_warp(self.warp_select.currentText())

        if not status:
            QtWidgets.QMessageBox.warning(self, 'Time Warp',
                                          'No objects selected to apply to warp or selected nodes'
                                          ' do not have any keyframes to warp.')

    def on_remove(self):
        """ On remove from warp check for selection.

        Returns:
            None
        """

        status = core.apply_warp(self.warp_select.currentText())

        if not status:
            QtWidgets.QMessageBox.warning(self, 'Time Warp',
                                          'No objects selected to remove from warp or selected nodes are not warped.')

    def on_delete(self):
        """ Action on delete of warp we need to fix the widget.

        Returns:
            None
        """

        current_warp = self.warp_select.currentText()

        core.delete_warp(current_warp)

        self.warp_select.removeItem(self.warp_select.findText(current_warp))

    def on_bake(self):
        """ Action on bake of warp we need to fix the widget.

        Returns:
            None
        """

        current_warp = self.warp_select.currentText()

        core.bake_warp(current_warp)

        self.warp_select.removeItem(self.warp_select.findText(current_warp))


def launch():
    """ Launch UI """

    global _WIDGET  # pylint: disable=global-statement

    if _WIDGET:
        _WIDGET.close()
        _WIDGET = None

    _WIDGET = TimeWarp()

    _WIDGET.show()


