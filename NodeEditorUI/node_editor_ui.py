import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
from PySide2 import QtWidgets

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

        # Modules section
        self.modules_title = QtWidgets.QLabel("Modules")
        self.modules_title.setStyleSheet("font-weight: bold;")
        self.modules_list = QtWidgets.QListWidget()
        self.modules_list.addItems([
            "TwoBoneIK",
            "splineSpineIK",
            "Control",
            "FKChain"
        ])
        self.modules_list.itemDoubleClicked.connect(self.add_node)

        self.modules_scroll_area = QtWidgets.QScrollArea()
        self.modules_scroll_area.setWidget(self.modules_list)
        self.modules_scroll_area.setWidgetResizable(True)

        # Addons section
        self.addons_title = QtWidgets.QLabel("Add-ons")
        self.addons_title.setStyleSheet("font-weight: bold;")
        self.addons_list = QtWidgets.QListWidget()
        self.addons_list.addItems([
            "Squash and Stretch"
        ])
        self.addons_list.itemDoubleClicked.connect(self.add_addon)

        self.addons_scroll_area = QtWidgets.QScrollArea()
        self.addons_scroll_area.setWidget(self.addons_list)
        self.addons_scroll_area.setWidgetResizable(True)

        # Add widgets to left column layout
        left_column_layout.addWidget(self.modules_title)
        left_column_layout.addWidget(self.modules_scroll_area, 1)
        left_column_layout.addWidget(self.addons_title)
        left_column_layout.addWidget(self.addons_scroll_area, 1)

        # === NODE EDITOR AREA ===
        self.node_editor_layout = QtWidgets.QVBoxLayout()
        self.node_editor = NodeEditor(self.node_editor_layout)

        # === MAIN HORIZONTAL LAYOUT ===
        main_layout = QtWidgets.QHBoxLayout()
        left_widget = QtWidgets.QWidget()
        left_widget.setLayout(left_column_layout)
        main_layout.addWidget(left_widget, 1)  # Smaller width

        right_widget = QtWidgets.QWidget()
        right_widget.setLayout(self.node_editor_layout)
        main_layout.addWidget(right_widget, 4)  # Wider area for navigation

        self.setLayout(main_layout)

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
    # Import the main window class
    from node_main_menu import NodeEditorMainWindow
    editor = NodeEditorMainWindow()
    editor.show()
