import os
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
from PySide2 import QtWidgets, QtCore, QtGui
import json

from node_editor_ui import NodeEditorUI
from node_editor import NodeEditor
from node_item import NodeItem
from node_node import *
from node_data_manager import NodeDataManager

from node_serialization import save_scene, load_scene


def get_maya_window():
    """
    Retrieve the Maya main window

    Returns:
        QtWidgets.QWidget: Maya's main window
    """
    ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(ptr), QtWidgets.QWidget)


class NodeEditorMainWindow(QtWidgets.QMainWindow):
    """
    Main window wrapper for the node editor with menu bar
    """
    
    # Keep track of all open windows
    open_windows = []
    
    # Keep track of the current file
    current_file = None
    is_modified = False

    def __init__(self, parent=get_maya_window()):
        """
        Initialize the node editor main window with menus

        Args:
            parent (QtWidgets.QWidget, optional): Parent window
        """
        super().__init__(parent)
        self.data_manager = NodeDataManager()
        self.setWindowTitle("Rigging Nodes")
        self.setGeometry(100, 100, 1200, 800)
        
        # Add this window to the list of open windows
        NodeEditorMainWindow.open_windows.append(self)

        # Create the original node editor UI as a widget
        self.node_editor_ui = NodeEditorUI(parent=None)  # No parent to avoid Maya-specific issues
        
        # Set the node editor UI as the central widget
        self.setCentralWidget(self.node_editor_ui)
        
        # Create menus
        self.create_menus()
        
        # Set up status bar
        self.statusBar().showMessage("Ready")
    
    def closeEvent(self, event):
        """
        Handle window close event

        Args:
            event: Close event
        """
        # Clear temp data when closing
        if hasattr(self, 'data_manager'):
            self.data_manager.clear_data()
        
        # Remove this window from the list of open windows
        if self in NodeEditorMainWindow.open_windows:
            NodeEditorMainWindow.open_windows.remove(self)
        
        # Make sure to close the embedded NodeEditorUI
        self.node_editor_ui.close()
        
        event.accept()

    def create_menus(self):
        """
        Create menu bar with File and Edit menus
        """
        # Create menu bar
        self.menu_bar = self.menuBar()
        
        # File menu
        self.file_menu = self.menu_bar.addMenu("File")
        
        # File menu actions
        self.new_action = QtWidgets.QAction("New", self)
        self.new_action.setShortcut("Ctrl+N")
        self.file_menu.addAction(self.new_action)
        
        self.open_action = QtWidgets.QAction("Open", self)
        self.open_action.setShortcut("Ctrl+O")
        self.file_menu.addAction(self.open_action)
        
        self.file_menu.addSeparator()
        
        self.save_action = QtWidgets.QAction("Save", self)
        self.save_action.setShortcut("Ctrl+S")
        self.file_menu.addAction(self.save_action)
        
        self.save_as_action = QtWidgets.QAction("Save As...", self)
        self.save_as_action.setShortcut("Ctrl+Shift+S")
        self.file_menu.addAction(self.save_as_action)
        
        self.file_menu.addSeparator()
        
        self.exit_action = QtWidgets.QAction("Exit", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.file_menu.addAction(self.exit_action)
        
        # Edit menu
        self.edit_menu = self.menu_bar.addMenu("Edit")
        
        # Edit menu actions
        self.undo_action = QtWidgets.QAction("Undo", self)
        self.undo_action.setShortcut("Ctrl+Z")
        self.edit_menu.addAction(self.undo_action)
        
        self.redo_action = QtWidgets.QAction("Redo", self)
        self.redo_action.setShortcut("Ctrl+Shift+Z")
        self.edit_menu.addAction(self.redo_action)
        
        self.edit_menu.addSeparator()
        
        self.delete_action = QtWidgets.QAction("Delete", self)
        self.delete_action.setShortcut("Delete")
        self.edit_menu.addAction(self.delete_action)
        
        # Connect menu actions
        self.connect_actions()
    
    def connect_actions(self):
        """
        Connect menu actions to methods
        """
        # File menu connections
        self.new_action.triggered.connect(self.new_file)
        self.open_action.triggered.connect(self.open_file)
        self.save_action.triggered.connect(self.save_file)
        self.save_as_action.triggered.connect(self.save_file_as)
        self.exit_action.triggered.connect(self.close)
        
        # Edit menu connections
        self.undo_action.triggered.connect(self.placeholder_action)
        self.redo_action.triggered.connect(self.placeholder_action)
        self.delete_action.triggered.connect(self.placeholder_action)
    
    def new_file(self):
        """
        Create a new node editor window while keeping the current one open
        """
        # Clear temp data before creating new window
        if hasattr(self, 'data_manager'):
            self.data_manager.clear_data()
        
        # Create a new instance of the main window
        new_window = NodeEditorMainWindow()
        
        # Offset the new window position slightly to avoid perfect overlap
        current_pos = self.pos()
        new_window.move(current_pos.x() + 30, current_pos.y() + 30)
        
        # Show the new window
        new_window.show()
        
        self.statusBar().showMessage("New editor window created", 2000)
    
    def open_file(self):
        """
        Open a node editor scene from a file
        """
        # Create a file dialog
        file_dialog = QtWidgets.QFileDialog(self, "Open Node Editor Scene", "", "JSON Files (*.json)")
        file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
        file_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        
        # Show the dialog
        if file_dialog.exec_() == QtWidgets.QDialog.Accepted:
            filename = file_dialog.selectedFiles()[0]
            scene = self.node_editor_ui.node_editor.scene()
            
            # Use the load_scene function with the selected filename
            if load_scene(scene, filename):
                # Clear existing temp data
                self.data_manager.clear_data()
                
                # Load the saved file data into temp
                with open(filename, 'r') as f:
                    saved_data = json.load(f)
                    self.data_manager.load_data(saved_data)
                
                self.statusBar().showMessage(f"Scene loaded successfully from {filename}", 2000)
                self.current_file = filename
                self.is_modified = False
                self.setWindowTitle(f"Rigging Nodes - {os.path.basename(filename)}")
            else:
                self.statusBar().showMessage("Failed to load scene", 2000)
        else:
            self.statusBar().showMessage("Load operation canceled", 2000)
    
    def save_file(self):
        """
        Save the current scene to a file
        """
        scene = self.node_editor_ui.node_editor.scene()
        
        # If we have a current file, save to it
        if self.current_file:
            if save_scene(scene, self.current_file):
                self.statusBar().showMessage(f"Scene saved successfully to {self.current_file}", 2000)
                self.is_modified = False
            else:
                self.statusBar().showMessage("Failed to save scene", 2000)
        else:
            # If no current file, do a Save As
            self.save_file_as()
    
    def save_file_as(self):
        """
        Save the current scene to a new file
        """
        # Create a file dialog
        file_dialog = QtWidgets.QFileDialog(self, "Save Node Editor Scene", "", "JSON Files (*.json)")
        file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        file_dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        file_dialog.setDefaultSuffix("json")
        
        # Show the dialog
        if file_dialog.exec_() == QtWidgets.QDialog.Accepted:
            filename = file_dialog.selectedFiles()[0]
            scene = self.node_editor_ui.node_editor.scene()
            
            # Add extension if needed
            if not filename.endswith('.json'):
                filename += '.json'
            
            # Use the save_scene function with the selected filename
            if save_scene(scene, filename):
                self.statusBar().showMessage(f"Scene saved successfully to {filename}", 2000)
                self.current_file = filename
                self.is_modified = False
                self.setWindowTitle(f"Rigging Nodes - {os.path.basename(filename)}")
            else:
                self.statusBar().showMessage("Failed to save scene", 2000)
        else:
            self.statusBar().showMessage("Save operation canceled", 2000)
    
    def placeholder_action(self):
        """
        Placeholder method for menu actions (for visual representation only)
        """
        sender = self.sender()
        self.statusBar().showMessage(f"{sender.text()} action triggered", 2000)


def show_node_editor_with_menu():
    """
    Show the node editor with menu bar
    """
    window = NodeEditorMainWindow()
    window.show()
    return window


# Run the node editor with menu
if __name__ == '__main__':
    show_node_editor_with_menu()
