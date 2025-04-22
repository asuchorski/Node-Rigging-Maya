from PySide2 import QtWidgets, QtCore, QtGui
from node_node import SocketTypeRegistry, NodeSocket
from node_item import *
from node_data_manager import NodeDataManager

class SocketItem(QtWidgets.QGraphicsEllipseItem):
    """
    Graphical representation of a node socket
    """

    def __init__(self, x, y, socket, parent=None):
        """
        Create a socket graphics item

        Args:
            x (float): X position
            y (float): Y position
            socket (NodeSocket): Associated node socket
            parent (QtWidgets.QGraphicsItem, optional): Parent item
        """
        super().__init__(x, y, 25, 25, parent)

        # Color-code sockets based on type and direction
        color_map = {
            "input": QtGui.QColor(130, 200, 220),
            "output": QtGui.QColor(220, 200, 130)
        }

        self.socket = socket
        socket.graphics_item = self

        # Set socket color based on input/output
        self.setBrush(QtGui.QBrush(color_map.get("input" if socket.is_input else "output",
                                                 QtGui.QColor(100, 100, 100))))
        self.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        self.setAcceptHoverEvents(True)
        

        # Optional: add socket name tooltip
        self.setToolTip(f"{socket.name} ({socket.type})")

    def socket_center(self):
        """
        Get the center point of the socket in scene coordinates

        Returns:
            QtCore.QPointF: Socket center point
        """
        return self.mapToScene(self.rect().center())

    def hoverEnterEvent(self, event):
        """
        Handle hover enter event for the socket

        Args:
            event (QtGui.QGraphicsSceneHoverEvent): Hover enter event
        """
        color_map = {
            "input": QtGui.QColor(200, 255, 255),
            "output": QtGui.QColor(255, 255, 200)
        }
        self.setBrush(QtGui.QBrush(color_map.get("input" if self.socket.is_input else "output",
                                                 QtGui.QColor(100, 100, 100))))
        
        
        #self.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
        #self.setPen(QtGui.QPen(QtGui.QColor(100, 100, 100),3))

    def hoverLeaveEvent(self, event):
        """
        Handle hover leave event for the socket

        Args:
            event (QtGui.QGraphicsSceneHoverEvent): Hover leave event
        """
        color_map = {
            "input": QtGui.QColor(130, 200, 220),
            "output": QtGui.QColor(220, 200, 130)
        }
        self.setBrush(QtGui.QBrush(color_map.get("input" if self.socket.is_input else "output",
                                                 QtGui.QColor(100, 100, 100))))
        self.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        


class ConnectionLine(QtWidgets.QGraphicsLineItem):
    """
    Graphical representation of a connection between sockets
    """

    def __init__(self, start_socket, end_socket):
        """
        Create a connection line between two sockets

        Args:
            start_socket (NodeSocket): Source socket
            end_socket (NodeSocket): Target socket
        """
        super().__init__()
        self.data_manager = NodeDataManager()

        # Verify socket node references
        if not hasattr(start_socket, 'node') or not hasattr(end_socket, 'node'):
            print(f"Socket node references: {start_socket.node}, {end_socket.node}")
            raise ValueError("Sockets must have node references")

        # Validate socket direction
        if start_socket.is_input == end_socket.is_input:
            raise ValueError("Cannot connect sockets of the same direction")

        # Determine source and target based on socket direction (input/output)
        source_socket = start_socket if not start_socket.is_input else end_socket
        target_socket = end_socket if source_socket is start_socket else start_socket

        # Validate socket types
        if not SocketTypeRegistry.is_compatible(source_socket.type, target_socket.type):
            raise ValueError(f"Incompatible socket types: {source_socket.type} vs {target_socket.type}")

        # Store socket references and graphics items
        self.start_socket = start_socket
        self.end_socket = end_socket
        self.start_graphics = start_socket.graphics_item
        self.end_graphics = end_socket.graphics_item

        # Connect sockets
        self.start_socket.connect(self.end_socket)

        # Styling
        self.setPen(QtGui.QPen(QtGui.QColor(130, 130, 130), 3))
        self.setZValue(-1)  # Ensure lines are behind nodes

        # Initial position update
        self.update_position()

        # Add connection to data manager
        self.data_manager.add_connection(self)

    def update_position(self):
        """
        Update connection line position based on socket graphics items
        """
        start_pos = self.start_graphics.socket_center()
        end_pos = self.end_graphics.socket_center()
        self.setLine(start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y())

    def remove(self):
        """
        Remove the connection and disconnect sockets
        """
        self.start_socket.disconnect(self.end_socket)

        # Remove from scene
        if self.scene():
            self.scene().removeItem(self)

        # Remove connection from data manager
        self.data_manager.remove_connection(self.start_socket, self.end_socket)


class CutLine(QtWidgets.QGraphicsLineItem):
    """
    Graphical representation of a cut line for removing connections
    """

    def __init__(self):
        super().__init__()
        self.setPen(QtGui.QPen(QtGui.QColor(200, 0, 0), 2, QtCore.Qt.DashLine))
        self.setZValue(10)  # Ensure cut line is on top of other items
