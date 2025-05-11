import os
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
from PySide2 import QtWidgets, QtCore, QtGui

from node_item import NodeItem
from node_addon import NodeAddon
from node_editor import NodeEditor
from node_node import *


def get_maya_window():
    """
    Retrieve the Maya main window

    Returns:
        QtWidgets.QWidget: Maya's main window
    """
    ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(ptr), QtWidgets.QWidget)


class NodeEditorUI(QtWidgets.QDialog):
    """
    Main UI for the node editor
    """

    def __init__(self, parent=get_maya_window()):
        """
        Initialize the node editor UI
        """
        super().__init__(parent)
        self.setWindowTitle("Rigging Nodes")
        self.setGeometry(100, 100, 1200, 800)

        # === LEFT COLUMN LAYOUT ===
        left_column_layout = QtWidgets.QVBoxLayout()

        self.modules_title = QtWidgets.QLabel("Modules")
        self.modules_title.setStyleSheet("font-weight: bold;")
        self.modules_list = QtWidgets.QListWidget()
        self.modules_list.addItems(["TwoBoneIK", "splineSpineIK", "Control", "FKChain"])
        self.modules_list.itemDoubleClicked.connect(self.add_node)

        self.modules_scroll_area = QtWidgets.QScrollArea()
        self.modules_scroll_area.setWidget(self.modules_list)
        self.modules_scroll_area.setWidgetResizable(True)

        self.addons_title = QtWidgets.QLabel("Add-ons")
        self.addons_title.setStyleSheet("font-weight: bold;")
        self.addons_list = QtWidgets.QListWidget()
        self.addons_list.addItems(["Squash and Stretch"])
        self.addons_list.itemDoubleClicked.connect(self.add_addon)

        self.addons_scroll_area = QtWidgets.QScrollArea()
        self.addons_scroll_area.setWidget(self.addons_list)
        self.addons_scroll_area.setWidgetResizable(True)

        left_column_layout.addWidget(self.modules_title)
        left_column_layout.addWidget(self.modules_scroll_area, 1)
        left_column_layout.addWidget(self.addons_title)
        left_column_layout.addWidget(self.addons_scroll_area, 1)

        # === TOP BAR WITH IMAGE BUTTONS ===
        top_bar_frame = QtWidgets.QFrame()
        top_bar_frame.setStyleSheet("background-color: #2a2a2a; border-bottom: 1px solid #444;")
        top_bar_frame.setFixedHeight(60)

        top_bar_layout = QtWidgets.QHBoxLayout(top_bar_frame)
        top_bar_layout.setSpacing(10)
        top_bar_layout.setContentsMargins(10, 10, 10, 10)

        button_filenames = [
            "stickynote.png", "loadskinweights.png", "saveskinweights.png",
            "dynin.png", "dynout.png", "template.png", "rerig.png", "connections.png", "help.png"
        ]

        tooltips = [
            "add a sticky note",
            "load skin weights to selected geom",
            "save skin weights of selected geom",
            "create dynamic in",
            "create dynamic out",
            "import template",
            "re-rig",
            "update connections",
            "help"
        ]

        image_dir = r"C:\\Users\\Asuch\\Desktop\\RiggingTool\\Imgs"

        for filename, tooltip in zip(button_filenames, tooltips):
            button = QtWidgets.QPushButton()
            button.setIcon(QtGui.QIcon(os.path.join(image_dir, filename)))
            button.setIconSize(QtCore.QSize(40, 40))
            button.setFixedSize(48, 48)
            button.setToolTip(tooltip)
            button.setStyleSheet("""
                QPushButton {
                    border: none;
                    background-color: transparent;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                    border-radius: 5px;
                }
            """)
            top_bar_layout.addWidget(button)

        # === NODE EDITOR AREA ===
        self.node_editor_layout = QtWidgets.QVBoxLayout()
        self.node_editor = NodeEditor(self.node_editor_layout)

        # Combine top bar and editor into a container
        editor_container = QtWidgets.QVBoxLayout()
        editor_container.setSpacing(0)
        editor_container.setContentsMargins(0, 0, 0, 0)
        editor_container.addWidget(top_bar_frame)
        editor_container.addLayout(self.node_editor_layout)

        # === MAIN HORIZONTAL LAYOUT ===
        main_layout = QtWidgets.QHBoxLayout()
        left_widget = QtWidgets.QWidget()
        left_widget.setLayout(left_column_layout)
        main_layout.addWidget(left_widget, 1)

        right_widget = QtWidgets.QWidget()
        right_widget.setLayout(editor_container)
        main_layout.addWidget(right_widget, 4)

        self.setLayout(main_layout)

        # Add Logo
        self.logo_label = QtWidgets.QLabel(self.node_editor)
        logo_path = os.path.join(image_dir, "rignodebanner.png")
        pixmap = QtGui.QPixmap(logo_path)
        self.logo_label.setPixmap(pixmap)
        self.logo_label.setScaledContents(True)

         # Keep logo pinned to bottom-right
        self.update_logo_position()
        self.node_editor.installEventFilter(self)


    def eventFilter(self, obj, event):
        if obj == self.node_editor and event.type() == QtCore.QEvent.Resize:
            self.update_logo_position()
        return super(NodeEditorUI, self).eventFilter(obj, event)

    def update_logo_position(self):
        margin = 10
        x = self.node_editor.width() - self.logo_label.width() - margin
        y = self.node_editor.height() - self.logo_label.height() - margin
        self.logo_label.move(x, y)


    def add_addon(self, item):
        addon_class_map = {
            "Squash and Stretch": SquashAndStretch
        }
        addon_class = addon_class_map.get(item.text(), BaseNode)
        addon = NodeAddon(0, 0, addon_class, scene=self.node_editor.scene())
        self.node_editor.scene().addItem(addon)

        if hasattr(addon, 'data_manager'):
            addon.data_manager.add_node(addon)
            print(f"Added node {addon.node_instance.name} to temporary JSON")

    def add_node(self, item):
        node_class_map = {
            "TwoBoneIK": TwoBoneIK,
            "splineSpineIK": splineSpineIK,
            "Control": Control,
            "FKChain": FKChain
        }
        node_class = node_class_map.get(item.text(), BaseNode)
        node = NodeItem(0, 0, node_class, scene=self.node_editor.scene())
        self.node_editor.scene().addItem(node)

        if hasattr(node, 'data_manager'):
            node.data_manager.add_node(node)
            print(f"Added node {node.node_instance.name} to temporary JSON")


def show_node_editor():
    """
    Show the node editor, ensuring only one instance
    """
    global editor
    try:
        editor.close()
    except:
        pass
    from node_main_menu import NodeEditorMainWindow
    editor = NodeEditorMainWindow()
    editor.show()
