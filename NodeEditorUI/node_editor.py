import math
from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtWidgets import QSizePolicy

from node_navigation import NodeNavigation
from node_graphics import SocketItem, ConnectionLine, CutLine
from node_item import NodeItem
from node_addon import NodeAddon
from node_node import *

class NodeEditor(NodeNavigation):
    """
    Main node editor view with navigation and grid background
    """

    def __init__(self, parent_layout, parent=None):
        """
        Initialize the node editor

        Args:
            parent_layout (QtWidgets.QLayout): Parent layout to add the node editor to
            parent (QtWidgets.QWidget, optional): Parent widget
        """
        super().__init__(parent)

        # Setup scene
        self.setScene(QtWidgets.QGraphicsScene(self))

        # Set the size policy to expand horizontally and vertically
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add the node editor to the parent layout
        parent_layout.addWidget(self)

        # Grid configuration
        self.gridSize = 50  # Size of small grid squares
        self.gridSquares = 5  # Number of small squares in a large grid square

        # Define light and dark grid pen colors
        self._pen_light = QtGui.QPen(QtGui.QColor(80, 80, 80, 50), 1, QtCore.Qt.SolidLine)
        self._pen_dark = QtGui.QPen(QtGui.QColor(10, 10, 10, 100), 2, QtCore.Qt.SolidLine)

        # Temporary connection drawing state
        self.temp_line = None
        self.start_socket = None

        # Cut line state
        self.cut_line = None
        self.cut_line_start = None

    def drawBackground(self, painter, rect):
        """
        Draw a grid background for the node editor

        Args:
            painter (QtGui.QPainter): Painter to draw with
            rect (QtCore.QRectF): Rectangle to draw in
        """
        # Ensure base background is drawn
        super().drawBackground(painter, rect)

        # Compute grid lines
        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))

        first_left = left - (left % self.gridSize)
        first_top = top - (top % self.gridSize)

        # Compute lines to be drawn
        lines_light, lines_dark = [], []
        for x in range(first_left, right, self.gridSize):
            if (x % (self.gridSize * self.gridSquares) != 0):
                lines_light.append(QtCore.QLine(x, top, x, bottom))
            else:
                lines_dark.append(QtCore.QLine(x, top, x, bottom))

        for y in range(first_top, bottom, self.gridSize):
            if (y % (self.gridSize * self.gridSquares) != 0):
                lines_light.append(QtCore.QLine(left, y, right, y))
            else:
                lines_dark.append(QtCore.QLine(left, y, right, y))

        # Draw the lines
        painter.setPen(self._pen_light)
        painter.drawLines(lines_light)

        painter.setPen(self._pen_dark)
        painter.drawLines(lines_dark)

    def detect_intersecting_connections(self, line):
        """
        Find connections intersecting with the cut line

        Args:
            line (QtCore.QLineF): Cut line to check for intersections

        Returns:
            list: List of connection lines intersecting the cut line
        """
        intersecting_connections = []
        for item in self.scene().items():
            if isinstance(item, ConnectionLine):
                connection_line = QtCore.QLineF(item.line())
                intersect_type = line.intersect(connection_line)[0]
                if intersect_type == QtCore.QLineF.BoundedIntersection:
                    intersecting_connections.append(item)
        return intersecting_connections

    def mousePressEvent(self, event):
        """
        Handle mouse press events for socket connections and cut line

        Args:
            event (QtGui.QMouseEvent): Mouse press event
        """
        modifiers = QtWidgets.QApplication.keyboardModifiers()

        if event.button() == QtCore.Qt.LeftButton:
            # Cut line drawing with Ctrl key
            if modifiers == QtCore.Qt.ControlModifier:
                scene_pos = self.mapToScene(event.pos())
                self.cut_line_start = scene_pos
                self.cut_line = CutLine()
                self.cut_line.setLine(QtCore.QLineF(scene_pos, scene_pos))
                self.scene().addItem(self.cut_line)
                return

            # Socket connection logic
            scene_pos = self.mapToScene(event.pos())
            items = self.scene().items(scene_pos)
            socket_item = next((item for item in items if isinstance(item, SocketItem)), None)

            if socket_item:
                if not self.temp_line:  # Start drawing connection
                    self.start_socket = socket_item.socket
                    self.temp_line = QtWidgets.QGraphicsLineItem(
                        socket_item.socket_center().x(),
                        socket_item.socket_center().y(),
                        scene_pos.x(),
                        scene_pos.y())
                    self.temp_line.setPen(QtGui.QPen(QtGui.QColor(190, 190, 190), 5))
                    self.scene().addItem(self.temp_line)
                else:  # Complete connection
                    if socket_item.socket != self.start_socket:
                        try:
                            connection = ConnectionLine(self.start_socket, socket_item.socket)
                            self.scene().addItem(connection)
                        except ValueError as e:
                            print(f"Connection Error: {e}")

                    # Clean up temporary line
                    self.scene().removeItem(self.temp_line)
                    self.temp_line = None
                    self.start_socket = None

        # Call parent's middle-mouse panning logic
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """
        Update temporary connection or cut line during drawing

        Args:
            event (QtGui.QMouseEvent): Mouse move event
        """
        scene_pos = self.mapToScene(event.pos())

        # Update temporary connection line
        if self.temp_line and self.start_socket:
            start_pos = self.start_socket.graphics_item.socket_center()
            self.temp_line.setLine(start_pos.x(), start_pos.y(),
                                   scene_pos.x(), scene_pos.y())

        # Update cut line
        if self.cut_line and self.cut_line_start:
            cutline = QtCore.QLineF(self.cut_line_start, scene_pos)
            self.cut_line.setLine(cutline)

        # Call parent's move event (handles panning)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """
        Handle mouse release for cut line and connection drawing

        Args:
            event (QtGui.QMouseEvent): Mouse release event
        """
        # Process cut line
        if self.cut_line and self.cut_line_start:
            cutline = QtCore.QLineF(self.cut_line_start, self.mapToScene(event.pos()))

            # Find and remove intersecting connections
            intersecting_connections = self.detect_intersecting_connections(cutline)
            for connection in intersecting_connections:
                connection.remove()

            # Remove cut line
            self.scene().removeItem(self.cut_line)
            self.cut_line = None
            self.cut_line_start = None

        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        """
        Handle key press events for item deletion

        Args:
            event (QtGui.QKeyEvent): Key press event
        """
        if event.key() in [QtCore.Qt.Key_Backspace, QtCore.Qt.Key_Delete]:
            # Collect items to remove
            items_to_remove = self.scene().selectedItems()

            for item in items_to_remove:
                if isinstance(item, NodeItem or NodeAddon):
                    # Remove only the connections specifically for this node's sockets
                    for socket in list(item.node_instance.input_sockets.values()) + \
                                  list(item.node_instance.output_sockets.values()):
                        for connection_socket in socket.connections[:]:
                            for scene_item in self.scene().items():
                                if isinstance(scene_item, ConnectionLine):
                                    if ((scene_item.start_socket == socket or
                                         scene_item.end_socket == socket)):
                                        scene_item.remove()
                    
                    # Remove node from temporary JSON before removing from scene
                    if hasattr(item, 'data_manager'):
                        item.data_manager.remove_node(item.node_id)
                    else:
                        print("Warning: Node has no data manager")

                    # Remove the node item from the scene
                    self.scene().removeItem(item)

                elif isinstance(item, ConnectionLine):
                    # Remove connection line
                    item.remove()
