from PySide2 import QtWidgets, QtGui, QtCore
import importlib
import maya.cmds as cmds
import sys

# Add the script path BEFORE importing
script_path = r"C:\\Users\\Asuch\\Desktop\\RiggingTool\\RiggingModules"
if script_path not in sys.path:
    sys.path.append(script_path)

# Reload py files used by modules
import functionality
importlib.reload(functionality)
from node_item import *

class NodeContextMenu(QtWidgets.QMenu):
    """
    Custom context menu for nodes in the node editor with dynamic module support
    """

    def __init__(self, node_item, parent=None):
        """
        Initialize the context menu for a specific node

        Args:
            node_item (NodeItem): The node item to create context menu for
            parent (QWidget, optional): Parent widget
        """
        super().__init__(parent)
        self.node_item = node_item

        # Module mapping for different node types
        self.module_map = {
            "TwoBoneIK": {
                "module_name": "IKarms",
                "template_method": "template",
                "rig_method": "twoBoneIK",
                "template_kwargs": {},
                "rig_kwargs": {"twistJoints" : 0, "addon": "NULL"}
            },
            "splineSpineIK": {
                "module_name": "splineSpineIK",
                "template_method": "template",
                "rig_method": "splineSpineIK",
                "template_kwargs": {"numControlJoints": 3},
                "rig_kwargs": {"numControlJoints": 3, "numJoints": 5, "addon": "NULL"}
            },
            "Control": {
                "module_name": "Control",
                "template_method": "template",
                "rig_method": "Control",
                "template_kwargs": {},
                "rig_kwargs": {"Control": "circle", "Colour": "red"}
            },
            "FKChain": {
                "module_name": "FKChain",
                "template_method": "template",
                "rig_method": "FKChain",
                "template_kwargs": {"numJoints": 3},
                "rig_kwargs": {"Control": "circle", "Colour": "red", "numJoints": 3}
            },



            "squashAndStretch": {
                "module_name": "addon_SquashAndStretch",
                "template_method": "template",
                "rig_method": "addon_SquashAndStretch",
                "template_kwargs": {},
                "rig_kwargs": {}
            }
        }
        
        # If this is a twoBoneIK node, update the module map with user inputs
        if type(self.node_item.node_instance).__name__ == "TwoBoneIK":
            twistJoints = self.node_item.node_instance.twistJoints
            addon = self.node_item.node_instance.addon
            

            self.module_map["TwoBoneIK"]["rig_kwargs"]["twistJoints"] = twistJoints
            self.module_map["TwoBoneIK"]["rig_kwargs"]["addon"] = addon
            

        # If this is a splineSpineIK node, update the module map with user inputs
        if type(self.node_item.node_instance).__name__ == "splineSpineIK":
            numControlJoints = self.node_item.node_instance.numControlJoints
            numJoints = self.node_item.node_instance.numJoints
            addon = self.node_item.node_instance.addon
            
            self.module_map["splineSpineIK"]["template_kwargs"]["numControlJoints"] = numControlJoints
            self.module_map["splineSpineIK"]["rig_kwargs"]["numControlJoints"] = numControlJoints
            self.module_map["splineSpineIK"]["rig_kwargs"]["numJoints"] = numJoints
            self.module_map["splineSpineIK"]["rig_kwargs"]["addon"] = addon

        # If this is a Control node, update the module map with user inputs
        if type(self.node_item.node_instance).__name__ == "Control":
            controlShape = self.node_item.node_instance.controlShape
            controlColour = self.node_item.node_instance.controlColour
            
            self.module_map["Control"]["rig_kwargs"]["Control"] = controlShape
            self.module_map["Control"]["rig_kwargs"]["Colour"] = controlColour

        # If this is a FKChain node, update the module map with user inputs
        if type(self.node_item.node_instance).__name__ == "FKChain":
            controlShape = self.node_item.node_instance.controlShape
            controlColour = self.node_item.node_instance.controlColour
            numJoints = self.node_item.node_instance.numJoints
            

            self.module_map["FKChain"]["template_kwargs"]["numJoints"] = numJoints
            self.module_map["FKChain"]["rig_kwargs"]["Control"] = controlShape
            self.module_map["FKChain"]["rig_kwargs"]["Colour"] = controlColour
            self.module_map["FKChain"]["rig_kwargs"]["numJoints"] = numJoints
            

        # Create actions
        self.import_template_action = self.addAction("Import Template")
        
        # Modify the Re-Rig action text based on selection
        scene = self.node_item.scene()
        selected_nodes = [item for item in scene.selectedItems() if hasattr(item, 'node_instance')]
        if len(selected_nodes) > 1:
            self.re_rig_action = self.addAction(f"Re-Rig ({len(selected_nodes)} selected nodes)")
        else:
            self.re_rig_action = self.addAction("Re-Rig")
            
        self.update_connections_action = self.addAction("Update Connections")

        # Connect actions to methods
        self.import_template_action.triggered.connect(self.import_template)
        self.re_rig_action.triggered.connect(self.re_rig)
        self.update_connections_action.triggered.connect(self.update_connections)

    def update_connections(self):
        """
        Update all connections in the scene
        """

        # Get the scene from the node item
        scene = self.node_item.scene()
        if not scene:
            return

        # Collect all connection lines in the scene
        connection_lines = [
            item for item in scene.items() 
            if hasattr(item, 'start_socket') and hasattr(item, 'end_socket')
        ]

        # Track successful and failed connections
        successful_connections = []
        failed_connections = []

        # Execute connections
        for connection in connection_lines:
            try:
                # Ensure both sockets have associated code
                if connection.start_socket.associated_code and connection.end_socket.associated_code:
                    # Determine source and target sockets
                    source_socket = connection.start_socket if not connection.start_socket.is_input else connection.end_socket
                    target_socket = connection.end_socket if source_socket is connection.start_socket else connection.start_socket

                    # Extract key (replace [1] with [-1] for input socket)
                    key = source_socket.associated_code.replace('[1]', '[-1]')
                    
                    # Call connection functionality
                    functionality.connect(
                        _out=source_socket.associated_code, 
                        _in=target_socket.associated_code, 
                        key=key
                    )
                    
                    successful_connections.append(
                        f"{source_socket.name} ({source_socket.associated_code}) -> "
                        f"{target_socket.name} ({target_socket.associated_code})"
                    )
            except Exception as e:
                failed_connections.append(
                    f"Connection Error: {connection.start_socket.name} to {connection.end_socket.name} - {str(e)}"
                )


    def import_template(self):
        """
        Import template for the specific node type
        """

        ## Create Base Groups If They Dont Exist ##
        if not cmds.objExists("RIG_TEMP_GRP_ALL"):
            cmds.select(clear=True)
            cmds.group(empty=True, name="RIG_TEMP_GRP_ALL")
            
        if not cmds.objExists("RIG_GRP_ALL"):
            cmds.select(clear=True)
            cmds.group(empty=True, name="RIG_GRP_ALL")

        node_type = type(self.node_item.node_instance).__name__
        node_name = self.node_item.node_instance.name
        
        try:
            # Retrieve module configuration
            module_config = self.module_map.get(node_type)
            
            if not module_config:
                raise ValueError(f"No module configuration found for {node_type}")
            
            # Dynamically import and reload module
            module = __import__(module_config['module_name'])
            importlib.reload(module)
            
            # Prepare kwargs
            template_kwargs = module_config.get('template_kwargs', {})
            template_kwargs['identifier'] = node_name
            
            # Call template function
            template_method = getattr(module, module_config['template_method'])
            template_method(**template_kwargs)
            

        except Exception as e:
            return

    def re_rig(self):
        """
        Re-rig the node(s) and update socket mappings
        If multiple nodes are selected, re-rig all of them
        """
        # Ensure base groups exist
        if not cmds.objExists("RIG_TEMP_GRP_ALL"):
            cmds.select(clear=True)
            cmds.group(empty=True, name="RIG_TEMP_GRP_ALL")
            
        if not cmds.objExists("RIG_GRP_ALL"):
            cmds.select(clear=True)
            cmds.group(empty=True, name="RIG_GRP_ALL")
        
        # Get the scene
        scene = self.node_item.scene()
        if not scene:
            return
            
        # Get all selected node items
        selected_nodes = [
            item for item in scene.selectedItems() 
            if hasattr(item, 'node_instance')
        ]
        
        # If no nodes are selected, default to the node that was right-clicked
        if not selected_nodes:
            selected_nodes = [self.node_item]
        
        # Print status for user
        if len(selected_nodes) > 1:
            print(f"Re-rigging {len(selected_nodes)} selected nodes...")
        else:
            print(f"Re-rigging node: {self.node_item.node_instance.name}")
        
        # Process each selected node
        for node_item in selected_nodes:
            try:
                node_type = type(node_item.node_instance).__name__
                node_name = node_item.node_instance.name
                
                # Skip if no module configuration exists for this node type
                module_config = self.module_map.get(node_type)
                if not module_config:
                    print(f"Skipping {node_name}: No module configuration found for {node_type}")
                    continue
                
                # Import the module
                module = __import__(module_config['module_name'])
                importlib.reload(module)
                
                # Prepare kwargs
                rig_kwargs = module_config.get('rig_kwargs', {})
                rig_kwargs['identifier'] = node_name
                
                # Call rig function and capture its return
                rig_method = getattr(module, module_config['rig_method'])
                connections = rig_method(**rig_kwargs)
                
                # Update socket associated codes with actual Maya item names
                for socket_name, socket in node_item.node_instance.input_sockets.items():
                    if socket.associated_code:
                        try:
                            # Evaluate the associated code in the context of the returned connections
                            actual_item_name = eval(socket.associated_code, {"__builtins__": None}, 
                                                   {"connectionsIKarms": connections, "connectionsSpineIK": connections, "connectionsControl": connections, "connectionsFKChain": connections})
                            
                            # Update the socket's associated code with the actual Maya item name
                            socket.associated_code = actual_item_name
                        except Exception as e:
                            print(f"Error updating socket {socket_name}: {e}")
                
                # Do the same for output sockets
                for socket_name, socket in node_item.node_instance.output_sockets.items():
                    if socket.associated_code:
                        try:
                            # Evaluate the associated code in the context of the returned connections
                            actual_item_name = eval(socket.associated_code, {"__builtins__": None}, 
                                                   {"connectionsIKarms": connections, "connectionsSpineIK": connections, "connectionsControl": connections, "connectionsFKChain": connections})
                            
                            # Update the socket's associated code with the actual Maya item name
                            socket.associated_code = actual_item_name
                        except Exception as e:
                            print(f"Error updating socket {socket_name}: {e}")
                
                # Process connections for this node
                self.process_node_connections(node_item)
                
                print(f"Successfully re-rigged: {node_name}")
                
            except Exception as e:
                print(f"Error re-rigging {node_item.node_instance.name}: {str(e)}")
        
        if len(selected_nodes) > 1:
            print("Finished re-rigging all selected nodes.")
    
    def process_node_connections(self, node_item):
        """
        Process connections for a specific node
        
        Args:
            node_item: The node item to process connections for
        """
        # Get the scene
        scene = node_item.scene()
        if not scene:
            return

        # Find all connection lines connected to this node
        connection_lines = [
            item for item in scene.items() 
            if hasattr(item, 'start_socket') and hasattr(item, 'end_socket') and
            (item.start_socket.node is node_item.node_instance or 
             item.end_socket.node is node_item.node_instance)
        ]

        # Track successful and failed connections
        successful_connections = []
        failed_connections = []

        # Execute connections
        for connection in connection_lines:
            try:
                # Ensure both sockets have associated code
                if connection.start_socket.associated_code and connection.end_socket.associated_code:
                    # Determine source and target sockets
                    source_socket = connection.start_socket if not connection.start_socket.is_input else connection.end_socket
                    target_socket = connection.end_socket if source_socket is connection.start_socket else connection.start_socket

                    # Call connection functionality
                    functionality.connect(
                        _out=source_socket.associated_code, 
                        _in=target_socket.associated_code
                    )
                    
                    successful_connections.append(
                        f"{source_socket.name} ({source_socket.associated_code}) -> "
                        f"{target_socket.name} ({target_socket.associated_code})"
                    )
            except Exception as e:
                failed_connections.append(
                    f"Connection Error: {connection.start_socket.name} to {connection.end_socket.name} - {str(e)}"
                )

        # Log the results
        if successful_connections:
            print(f"Connections for {node_item.node_instance.name}:")
            for conn in successful_connections:
                print(f"  Success: {conn}")
                
        if failed_connections:
            print(f"Failed connections for {node_item.node_instance.name}:")
            for conn in failed_connections:
                print(f"  Failed: {conn}")
            
    def delete_node(self):
        """
        Delete the node and all its connections
        """
        # Disconnect all sockets
        for socket in list(self.node_item.node_instance.input_sockets.values()) + \
                      list(self.node_item.node_instance.output_sockets.values()):
            socket.disconnect()

        # Remove from scene
        scene = self.node_item.scene()
        if scene:
            scene.removeItem(self.node_item)