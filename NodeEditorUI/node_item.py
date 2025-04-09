import sys
import math
from PySide2 import QtWidgets, QtCore, QtGui
from maya import cmds
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance

from node_graphics import SocketItem, ConnectionLine
from node_context_menu import NodeContextMenu
from node_node import *
from node_data_manager import NodeDataManager

class NodeItem(QtWidgets.QGraphicsRectItem):
    """
    Graphical representation of a node
    """

    def __init__(self, x, y, node_class, name=None, scene=None):
        """
        Create a visual node representation

        Args:
            x (float): X position
            y (float): Y position
            node_class (type): Node class to instantiate
            name (str, optional): Node name
            scene (QtWidgets.QGraphicsScene, optional): Scene to check for unique names
        """
        # Default dimensions
        width, height = 250, 300

        super().__init__(x, y, width, height)

        # Ensure unique name in the scene
        if scene:
            name = self._generate_unique_name(scene, name or node_class.__name__)
        else:
            name = name or node_class.__name__

        # Create node instance
        self.node_instance = node_class(name)
        self.node_id = id(self)  # Add unique identifier
        self.data_manager = NodeDataManager()  # Initialize data manager

        # Add node to temporary JSON immediately upon creation
        self.data_manager.add_node(self)
        print(f"Added node {self.node_instance.name} to temporary JSON")

        # Node styling
        self.setBrush(QtGui.QBrush(QtGui.QColor(80, 80, 80)))
        self.setFlags(
            QtWidgets.QGraphicsItem.ItemIsMovable |
            QtWidgets.QGraphicsItem.ItemIsSelectable |
            QtWidgets.QGraphicsItem.ItemSendsGeometryChanges
        )

        # Node title
        self.text = QtWidgets.QGraphicsTextItem(name, self)
        self.text.setPos(x + 5, y + 5)
        
        # Create a button that opens a Maya input dialog
        self.input_button = QtWidgets.QPushButton("Rename")
        self.input_button.setStyleSheet("""
            QPushButton {
                background-color: #505050;
                color: white;
                border: 0px solid #303030;
                padding: 2px;
                min-width: 233px;
            }
            QPushButton:hover {
                background-color: #606060;
            }
        """)
        
        # Create a proxy for the button
        self.button_proxy = QtWidgets.QGraphicsProxyWidget(self)
        self.button_proxy.setWidget(self.input_button)
        self.button_proxy.setPos(5, 30)
        
        # Connect to Maya's native dialog
        self.input_button.clicked.connect(self._open_maya_input_dialog)
        
        # Store notes in the node instance
        if not hasattr(self.node_instance, 'notes'):
            self.node_instance.notes = ""
            
        # Check if this is a splineSpineIK node and add specific UI controls
        if isinstance(self.node_instance, splineSpineIK) and hasattr(self.node_instance, 'controlWidget'):
            # Create a proxy for the spineIK controls
            self.spine_controls_proxy = QtWidgets.QGraphicsProxyWidget(self)
            self.spine_controls_proxy.setWidget(self.node_instance.controlWidget)
            self.spine_controls_proxy.setPos(5, 70)  # Position below the rename button
            self.setBrush(QtGui.QBrush(QtGui.QColor(68, 68, 68)))

        # Check if this is a Control node and add specific UI controls
        if isinstance(self.node_instance, Control) and hasattr(self.node_instance, 'controlWidget'):
            # Create a proxy for the Control controls
            self.control_controls_proxy = QtWidgets.QGraphicsProxyWidget(self)
            self.control_controls_proxy.setWidget(self.node_instance.controlWidget)
            self.control_controls_proxy.setPos(5, 70)  # Position below the rename button
            self.setBrush(QtGui.QBrush(QtGui.QColor(68, 68, 68)))

        # Check if this is a TwoBoneIK node and add specific UI controls
        if isinstance(self.node_instance, TwoBoneIK) and hasattr(self.node_instance, 'controlWidget'):
            # Create a proxy for the Control controls
            self.twist_controls_proxy = QtWidgets.QGraphicsProxyWidget(self)
            self.twist_controls_proxy.setWidget(self.node_instance.controlWidget)
            self.twist_controls_proxy.setPos(5, 70)  # Position below the rename button
            self.setBrush(QtGui.QBrush(QtGui.QColor(68, 68, 68)))

        # Check if this is a FKChain node and add specific UI controls
        if isinstance(self.node_instance, FKChain) and hasattr(self.node_instance, 'controlWidget'):
            # Create a proxy for the Control controls
            self.fkChain_controls_proxy = QtWidgets.QGraphicsProxyWidget(self)
            self.fkChain_controls_proxy.setWidget(self.node_instance.controlWidget)
            self.fkChain_controls_proxy.setPos(5, 70)  # Position below the rename button
            self.setBrush(QtGui.QBrush(QtGui.QColor(68, 68, 68)))
            


        # Create socket items
        self._create_sockets()

    def _open_maya_input_dialog(self):
        """
        Open Maya's native input dialog to edit the node name
        """
        result = cmds.promptDialog(
            title='Edit Node Name',
            message='Enter Name:',
            text=self.node_instance.name,
            button=['OK', 'Cancel'],
            defaultButton='OK',
            cancelButton='Cancel'
        )
        
        if result == 'OK':
            # Get the new name from the dialog
            new_name = cmds.promptDialog(query=True, text=True)
            
            # Check for uniqueness
            if self.scene():
                new_name = self._ensure_unique_name(new_name)
                
            # Update the node
            self.node_instance.name = new_name
            self.text.setPlainText(new_name)
            self.line_edit.setText(new_name)
            self.data_manager.add_node(self)  # Update node data in temp file

    def _ensure_unique_name(self, name):
        """
        Ensure the name is unique in the scene
        """
        # Check other nodes to ensure uniqueness
        existing_names = [
            item.node_instance.name
            for item in self.scene().items()
            if isinstance(item, NodeItem) and item != self
        ]

        # If name already exists, append a number
        base_name = name
        counter = 1
        while name in existing_names:
            name = f"{base_name}{counter}"
            counter += 1
            
        return name

    def _generate_unique_name(self, scene, base_name):
        """
        Generate a unique name for the node in the given scene
        """
        # Get the current class type (since NodeItem is now imported)
        node_item_class = self.__class__
        
        # Function to check if a node name exists in the scene
        def name_exists(check_name):
            return any(
                isinstance(item, node_item_class) and
                hasattr(item, 'node_instance') and
                item.node_instance.name == check_name
                for item in scene.items()
            )

        # If base name doesn't exist, return it
        if not name_exists(base_name):
            return base_name

        # Try adding numbers to create a unique name
        counter = 1
        while name_exists(f"{base_name}{counter}"):
            counter += 1

        return f"{base_name}{counter}"

    def _create_sockets(self):
        """
        Dynamically create socket graphics based on node's sockets
        """
        # Input sockets on the left
        input_sockets = list(self.node_instance.input_sockets.values())
        input_spacing = self.rect().height() / (len(input_sockets) + 1)

        for i, socket in enumerate(input_sockets, 1):
            SocketItem(
                self.rect().left() - 10,
                self.pos().y() + input_spacing * i,
                socket,
                self
            )

        # Output sockets on the right
        output_sockets = list(self.node_instance.output_sockets.values())
        output_spacing = self.rect().height() / (len(output_sockets) + 1)

        for i, socket in enumerate(output_sockets, 1):
            SocketItem(
                self.rect().right() - 10,
                self.pos().y() + output_spacing * i,
                socket,
                self
            )

    def mousePressEvent(self, event):
        """
        Handle mouse press events
        """
        # Just use the default handler for selection and movement
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """
        Handle mouse release events
        """
        # Ensure default node interaction
        super().mouseReleaseEvent(event)

    def contextMenuEvent(self, event):
        """
        Show context menu when right-clicking on a node

        Args:
            event (QtWidgets.QGraphicsSceneContextMenuEvent): Context menu event
        """
        context_menu = NodeContextMenu(self)
        context_menu.exec_(event.screenPos())

    def itemChange(self, change, value):
        """
        Handle item changes, specifically node movement

        Args:
            change (QtWidgets.QGraphicsItem.GraphicsItemChange): Type of change
            value (object): New value

        Returns:
            object: Modified value
        """
        if change == QtWidgets.QGraphicsItem.ItemPositionHasChanged:
            # Update socket positions and connections when node moves
            for socket_item in self.childItems():
                if isinstance(socket_item, SocketItem):
                    for connection in socket_item.socket.connections:
                        # Find and update all related connection lines
                        for scene_item in self.scene().items():
                            if isinstance(scene_item, ConnectionLine):
                                if (scene_item.start_socket == socket_item.socket or
                                        scene_item.end_socket == socket_item.socket):
                                    scene_item.update_position()
            # Update node data in temp file
            self.data_manager.add_node(self)

        return super().itemChange(change, value)

    def delete_node(self):
        """Delete the node and all its connections"""
        # Remove from temporary JSON
        if hasattr(self, 'data_manager'):
            self.data_manager.remove_node(self.node_id)
        else:
            print("Warning: Node has no data manager")
            
        # Disconnect all sockets
        for socket in list(self.node_instance.input_sockets.values()) + \
                      list(self.node_instance.output_sockets.values()):
            socket.disconnect_all()
        
        # Remove the node item from the scene
        self.scene().removeItem(self)
