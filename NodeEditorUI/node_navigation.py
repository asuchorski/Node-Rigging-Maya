from PySide2 import QtWidgets, QtCore, QtGui

class NodeNavigation(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Enhanced rendering
        self.setRenderHint(QtGui.QPainter.Antialiasing)

        # Expanded scene rect
        self.setSceneRect(-10000, -10000, 20000, 20000)

        # Scrollbar policies
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        # View settings
        self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)

        # Navigation state
        self.is_panning = False
        self.pan_start_pos = None
        self.last_pan_pos = None
        
        # Rubber band selection state
        self.is_rubber_band_selecting = False
        self.rubber_band_start_pos = None
        self.rubber_band = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self)
        
        # Custom style for rubber band
        palette = QtGui.QPalette()
        palette.setBrush(QtGui.QPalette.Highlight, QtGui.QBrush(QtGui.QColor(255, 255, 255, 255)))
        self.rubber_band.setPalette(palette)

    def wheelEvent(self, event):
        """
        Handle zoom with mouse wheel, keeping mouse position consistent
        """
        # Preserve zoom behavior with mouse position
        current_pos = self.mapToScene(event.pos())

        # Zoom factor (adjust these values to change zoom speed)
        zoom_in_factor = 1.1
        zoom_out_factor = 1 / zoom_in_factor
        zoom_factor = zoom_in_factor if event.angleDelta().y() > 0 else zoom_out_factor

        # Apply zoom
        self.scale(zoom_factor, zoom_factor)

        # Adjust view to keep mouse position consistent
        new_pos = self.mapToScene(event.pos())
        delta = new_pos - current_pos
        self.translate(delta.x(), delta.y())

    def mousePressEvent(self, event):
        """
        Handle panning start with middle mouse button
        Handle rubber band selection with left mouse button
        """
        # Check for middle mouse button (panning)
        if event.button() == QtCore.Qt.MiddleButton:
            # Start panning
            self.is_panning = True
            self.setCursor(QtCore.Qt.ClosedHandCursor)
            self.pan_start_pos = event.pos()
            self.last_pan_pos = event.pos()
            super().mousePressEvent(event)  # Let parent handle other aspects
            return
            
        # Check for left mouse button (selection)
        if event.button() == QtCore.Qt.LeftButton:
            # Convert mouse position to scene coordinates
            scene_pos = self.mapToScene(event.pos())
            
            # Check if the click is on an empty area (no items)
            item_at_click = self.scene().itemAt(scene_pos, self.transform())
            
            # If clicking on empty space, start rubber band selection
            if not item_at_click:
                self.is_rubber_band_selecting = True
                self.rubber_band_start_pos = event.pos()
                self.rubber_band.setGeometry(QtCore.QRect(self.rubber_band_start_pos, QtCore.QSize()))
                self.rubber_band.show()
                return  # Don't pass to parent handler
                
        # Pass other events to parent handler
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """
        Handle panning movement and rubber band selection
        """
        # Handle rubber band selection
        if self.is_rubber_band_selecting and self.rubber_band_start_pos is not None:
            # Update rubber band geometry
            selection_rect = QtCore.QRect(self.rubber_band_start_pos, event.pos()).normalized()
            self.rubber_band.setGeometry(selection_rect)
            return  # Don't pass to parent handler for rubber band selection
            
        # Improved, stable panning logic
        if self.is_panning and self.pan_start_pos is not None:
            # Calculate pan delta directly from screen coordinates
            pan_delta = event.pos() - self.last_pan_pos

            # Translate view using delta
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - pan_delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - pan_delta.y()
            )

            # Update last pan position
            self.last_pan_pos = event.pos()

        # Pass other events to parent handler
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """
        Handle panning end and rubber band selection completion
        """
        # Handle rubber band selection completion
        if event.button() == QtCore.Qt.LeftButton and self.is_rubber_band_selecting:
            # Get the rubber band rectangle in scene coordinates
            selection_rect = self.mapToScene(self.rubber_band.geometry()).boundingRect()
            
            # Hide rubber band
            self.rubber_band.hide()
            
            # Select all items within the selection rectangle
            self.select_nodes_in_rect(selection_rect)
            
            # Reset rubber band selection state
            self.is_rubber_band_selecting = False
            self.rubber_band_start_pos = None
            
            return  # Don't pass to parent handler for rubber band selection
            
        # Handle panning end
        if event.button() == QtCore.Qt.MiddleButton:
            # Reset panning state
            self.is_panning = False
            self.setCursor(QtCore.Qt.ArrowCursor)
            self.pan_start_pos = None
            self.last_pan_pos = None

        # Pass other events to parent handler
        super().mouseReleaseEvent(event)
        
    def select_nodes_in_rect(self, rect):
        """
        Select all node items that fall within the given rectangle
        
        Args:
            rect (QRectF): Rectangle in scene coordinates
        """
        if not self.scene():
            return
            
        # Get all items in the scene
        all_items = self.scene().items()
        
        # Filter for node items (NodeItem instances) within the rectangle
        # Assuming node items are instances that have a 'node_instance' attribute
        nodes_in_rect = [
            item for item in all_items 
            if hasattr(item, 'node_instance') and 
            rect.intersects(item.sceneBoundingRect())
        ]
        
        # If shift is not pressed, clear the current selection first
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if not modifiers & QtCore.Qt.ShiftModifier:
            self.scene().clearSelection()
        
        # Select the nodes
        for node in nodes_in_rect:
            node.setSelected(True)