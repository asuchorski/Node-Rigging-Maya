import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
from PySide2 import QtWidgets

from node_item import NodeItem
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

        Args:
            parent (QtWidgets.QWidget, optional): Parent window
        """
        super().__init__(parent)
        self.setWindowTitle("Rigging Nodes")
        self.setGeometry(100, 100, 1200, 800)

        # Node list for creating nodes
        self.node_list = QtWidgets.QListWidget()
        self.node_list.addItems([
            "TwoBoneIK",
            "splineSpineIK",
            "Control",
            "FKChain"
        ])
        self.node_list.itemDoubleClicked.connect(self.add_node)

        # Main node editor view
        self.node_editor = NodeEditor()

        # Layout
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.node_list, 1)
        layout.addWidget(self.node_editor, 4)
        self.setLayout(layout)

    def add_node(self, item):
        """
        Add a new node to the editor

        Args:
            item (QtWidgets.QListWidgetItem): Selected node type
        """
        # Dynamically create node based on selected type
        node_class_map = {
            "TwoBoneIK": TwoBoneIK,
            "splineSpineIK": splineSpineIK,
            "Control": Control,
            "FKChain": FKChain
        }
        node_class = node_class_map.get(item.text(), BaseNode)

        # Create node at a default position, passing the scene for unique naming
        node = NodeItem(0, 0, node_class, scene=self.node_editor.scene())
        self.node_editor.scene().addItem(node)

        # Add node to temporary JSON immediately after creation
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
