import os
import json
from PySide2 import QtCore

class NodeDataManager:
    """
    Manages temporary storage of node data during editor session
    """
    
    def __init__(self):
        self.temp_file_path = os.path.join(os.path.dirname(__file__), 'temp_node_data.json')
        self.node_data = {
            'nodes': [],
            'connections': []
        }
        self._initialize_temp_file()
    
    def _initialize_temp_file(self):
        """Initialize or load the temporary JSON file"""
        if os.path.exists(self.temp_file_path):
            try:
                with open(self.temp_file_path, 'r') as f:
                    self.node_data = json.load(f)
            except:
                self._save_temp_data()
        else:
            self._save_temp_data()
    
    def _save_temp_data(self):
        """Save current data to temporary file"""
        with open(self.temp_file_path, 'w') as f:
            json.dump(self.node_data, f, indent=2)
    
    def add_node(self, node_item):
        """Add or update node data"""
        node_data = {
            'name': node_item.node_instance.name,
            'type': node_item.node_instance.__class__.__name__,
            'id': node_item.node_id,
            'position': {
                'x': node_item.pos().x(),
                'y': node_item.pos().y()
            },
            'sockets': {
                'input': {},
                'output': {}
            },
            'parameters': {}
        }
        
        # Store socket data
        for name, socket in node_item.node_instance.input_sockets.items():
            node_data['sockets']['input'][name] = {
                'type': socket.type,
                'associated_code': socket.associated_code,
                'connections': []
            }
        
        for name, socket in node_item.node_instance.output_sockets.items():
            node_data['sockets']['output'][name] = {
                'type': socket.type,
                'associated_code': socket.associated_code,
                'connections': []
            }
        
        # Store special parameters for splineSpineIK
        if hasattr(node_item.node_instance, 'numControlJoints'):
            node_data['parameters']['numControlJoints'] = node_item.node_instance.numControlJoints
        if hasattr(node_item.node_instance, 'numJoints'):
            node_data['parameters']['numOfJoints'] = node_item.node_instance.numJoints
        if hasattr(node_item.node_instance, 'notes'):
            node_data['parameters']['notes'] = node_item.node_instance.notes
        
        # Update or add node data
        self.node_data['nodes'] = [n for n in self.node_data['nodes'] if n['id'] != node_item.node_id]
        self.node_data['nodes'].append(node_data)
        self._save_temp_data()
    
    def add_connection(self, connection_line):
        """Add or update connection data"""
        connection_data = {
            'start_node': connection_line.start_socket.node.name,
            'end_node': connection_line.end_socket.node.name,
            'start_socket': connection_line.start_socket.name,
            'end_socket': connection_line.end_socket.name,
            'start_socket_type': connection_line.start_socket.type,
            'end_socket_type': connection_line.end_socket.type,
            'start_associated_code': connection_line.start_socket.associated_code,
            'end_associated_code': connection_line.end_socket.associated_code
        }
        
        self.node_data['connections'].append(connection_data)
        self._save_temp_data()
    
    def remove_node(self, node_id):
        """Remove node data"""
        self.node_data['nodes'] = [n for n in self.node_data['nodes'] if n['id'] != node_id]
        self._save_temp_data()
    
    def remove_connection(self, start_socket, end_socket):
        """Remove connection data"""
        self.node_data['connections'] = [
            c for c in self.node_data['connections']
            if not (c['start_socket'] == start_socket.name and c['end_socket'] == end_socket.name)
        ]
        self._save_temp_data()
    
    def get_data(self):
        """Get current node editor data"""
        return self.node_data
    
    def load_data(self, data):
        """
        Load data into temp file
        
        Args:
            data (dict): Data to load into temp file
        """
        self.node_data = data
        self._save_temp_data()
        print(f"Loaded {len(data.get('nodes', []))} nodes and {len(data.get('connections', []))} connections into temp file")

    def clear_data(self):
        """Clear all temporary data"""
        self.node_data = {
            'nodes': [],
            'connections': []
        }
        self._save_temp_data()
