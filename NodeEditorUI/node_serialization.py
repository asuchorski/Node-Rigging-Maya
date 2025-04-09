import os
import json
from PySide2 import QtWidgets, QtCore
from node_data_manager import NodeDataManager
from node_node import *
from node_context_menu import *

class NodeEditorSerializer:
    def __init__(self):
        super().__init__()
        self.data_manager = NodeDataManager()

    @staticmethod
    def save_scene(scene, filename=None):
        """
        Save the current scene to a JSON file
        
        Args:
            scene (QtWidgets.QGraphicsScene): The scene to save
            filename (str, optional): Path to save file. If None, shows a file dialog
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            # Get data from manager
            scene_data = NodeDataManager().get_data()
            
            # Save to file
            with open(filename, 'w') as f:
                json.dump(scene_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving scene: {e}")
            return False

    @staticmethod
    def load_scene(scene, filename=None):
        """
        Load a scene from a JSON file
        
        Args:
            scene (QtWidgets.QGraphicsScene): The scene to load into
            filename (str, optional): Path to load file. If None, shows a file dialog
            
        Returns:
            bool: True if load was successful, False otherwise
        """
        # If no filename provided, ask for one
        if not filename:
            dialog = QtWidgets.QFileDialog(None, "Load Node Editor Scene", "", "JSON Files (*.json)")
            dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
            dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
            
            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                filename = dialog.selectedFiles()[0]
            else:
                return False  # User canceled
        
        # Clear existing scene
        scene.clear()
        
        # Load data from JSON file
        try:
            with open(filename, 'r') as f:
                scene_data = json.load(f)
            print(f"Loaded scene data from {filename}")
            print(f"Found {len(scene_data.get('nodes', []))} nodes and {len(scene_data.get('connections', []))} connections")
        except Exception as e:
            print(f"Error loading scene: {e}")
            return False
        
        # Map for node type names to classes
        node_class_map = {
            "TwoBoneIK": TwoBoneIK,
            "splineSpineIK": splineSpineIK,
            "Control": Control,
            "BaseNode": BaseNode,
            "FKChain": FKChain
        }
        
        # Map to keep track of created nodes by name
        created_nodes = {}
        
        # Create nodes
        for node_data in scene_data.get('nodes', []):
            try:
                # Get node class
                node_type = node_data.get('type', 'BaseNode')
                node_class = node_class_map.get(node_type)
                
                if not node_class:
                    print(f"Unknown node type: {node_type}, using BaseNode")
                    node_class = BaseNode
                
                # Create node
                node_item = NodeItem(
                    node_data['position']['x'],
                    node_data['position']['y'],
                    node_class,
                    scene=scene,
                    name=node_data['name']
                )
                
                # Create node with stored parameters
                if isinstance(node_item.node_instance, splineSpineIK):
                    if 'parameters' in node_data:
                        params = node_data['parameters']
                        if 'numControlJoints' in params:
                            node_item.node_instance.numControlJoints = params['numControlJoints']
                            if hasattr(node_item.node_instance, 'controlJointsCombo'):
                                node_item.node_instance.controlJointsCombo.setCurrentText(
                                    str(params['numControlJoints']))
                        if 'numOfJoints' in params:
                            node_item.node_instance.numJoints = params['numOfJoints']
                            if hasattr(node_item.node_instance, 'jointsSpinBox'):
                                node_item.node_instance.jointsSpinBox.setValue(
                                    params['numOfJoints'])
                        if 'notes' in params:
                            node_item.node_instance.notes = params['notes']
                
                # Add more parameter handling for future node types here
                
                # Add node to scene
                scene.addItem(node_item)
                
                # Store node for connection creation
                created_nodes[node_data['id']] = node_item
                print(f"Created node: {node_data['name']} of type {node_type}")
            
            except Exception as e:
                print(f"Error creating node {node_data.get('name', 'unknown')}: {e}")
        
        # Create connections
        for connection_data in scene_data.get('connections', []):
            try:
                start_node_id = connection_data['start_node']
                end_node_id = connection_data['end_node']
                
                start_node_item = next((node for node in created_nodes.values() if node.node_id == start_node_id), None)
                end_node_item = next((node for node in created_nodes.values() if node.node_id == end_node_id), None)
                
                if not start_node_item:
                    print(f"Start node not found: {start_node_id}")
                    continue
                    
                if not end_node_item:
                    print(f"End node not found: {end_node_id}")
                    continue
                
                # Find socket objects by name
                start_socket = None
                end_socket = None
                
                # Check output sockets of start node
                for socket in start_node_item.node_instance.output_sockets.values():
                    if socket.name == connection_data['start_socket']:
                        start_socket = socket
                        break
                
                # If not found, check input sockets
                if not start_socket:
                    for socket in start_node_item.node_instance.input_sockets.values():
                        if socket.name == connection_data['start_socket']:
                            start_socket = socket
                            break
                
                # Check input sockets of end node
                for socket in end_node_item.node_instance.input_sockets.values():
                    if socket.name == connection_data['end_socket']:
                        end_socket = socket
                        break
                
                # If not found, check output sockets
                if not end_socket:
                    for socket in end_node_item.node_instance.output_sockets.values():
                        if socket.name == connection_data['end_socket']:
                            end_socket = socket
                            break
                
                # Create connection if sockets found
                if start_socket and end_socket:
                    try:
                        # Restore socket associated codes
                        start_socket.associated_code = connection_data['start_associated_code']
                        end_socket.associated_code = connection_data['end_associated_code']

                        connection = ConnectionLine(start_socket, end_socket)
                        scene.addItem(connection)
                        print(f"Created connection from {start_node_id}.{connection_data['start_socket']} to {end_node_id}.{connection_data['end_socket']}")
                    except ValueError as e:
                        print(f"Error creating connection: {e}")
                else:
                    if not start_socket:
                        print(f"Start socket not found: {connection_data['start_socket']} on node {start_node_id}")
                    if not end_socket:
                        print(f"End socket not found: {connection_data['end_socket']} on node {end_node_id}")
            
            except Exception as e:
                print(f"Error creating connection: {e}")
        
        print(f"Scene loaded successfully from {filename}")
        return True

# Use these utility functions to simplify file operations
def save_scene(scene, filename=None):
    """Utility function to save a scene"""
    return NodeEditorSerializer.save_scene(scene, filename)

def load_scene(scene, filename=None):
    """Utility function to load a scene"""
    return NodeEditorSerializer.load_scene(scene, filename)
