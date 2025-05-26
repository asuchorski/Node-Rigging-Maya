from PySide2 import QtWidgets, QtGui, QtCore
import importlib
import sys

# Add the script path BEFORE importing
script_path = r"C:\\Users\\Asuch\\Desktop\\RiggingTool\\RiggingModules"
image_path = r"C:\\Users\\Asuch\\Desktop\\RiggingTool\\Imgs\\"
if script_path not in sys.path:
    sys.path.append(script_path)

# Reload py files uesd by modules
import functionality
importlib.reload(functionality)

class SocketTypeRegistry:
    """
    Manages socket type compatibility and inheritance
    """
    _type_hierarchy = {
        'any': [],
        'numeric': ['int', 'float'],
        'vector': ['point', 'direction'],
        'transform': ['matrix'],
        'matrix': []
    }

    @classmethod
    def is_compatible(cls, source_type, target_type):
        """
        Check if source type can connect to target type

        Args:
            source_type (str): Type of source socket
            target_type (str): Type of target socket

        Returns:
            bool: Whether the types are compatible
        """
        # 'any' type can connect to anything
        if source_type == 'any' or target_type == 'any':
            return True

        # Direct match
        if source_type == target_type:
            return True

        # Check type hierarchy
        for hierarchy_type, subtypes in cls._type_hierarchy.items():
            if source_type == hierarchy_type and target_type in subtypes:
                return True
            if target_type == hierarchy_type and source_type in subtypes:
                return True

        return False

class NodeSocket:
    def __init__(self, name, socket_type="any", is_input=True, associated_code=None):
        self.name = name
        self.type = socket_type
        self.is_input = is_input
        self.associated_code = associated_code
        self.connections = []
        self.graphics_item = None
        self.node = None  # Reference to parent node

    def connect(self, other_socket):
        """
        Connect this socket to another socket and execute associated functionality

        Args:
            other_socket (NodeSocket): Socket to connect to

        Raises:
            ValueError: If sockets are incompatible
        """
        # Check socket direction
        if self.is_input == other_socket.is_input:
            raise ValueError("Cannot connect sockets of the same direction")

        # Determine source and target sockets
        source_socket = other_socket if self.is_input else self
        target_socket = self if self.is_input else other_socket

        # Check type compatibility
        if not SocketTypeRegistry.is_compatible(source_socket.type, target_socket.type):
            raise ValueError(f"Incompatible socket types: {source_socket.type} vs {target_socket.type}")

        # Prevent duplicate connections
        if other_socket not in self.connections:
            self.connections.append(other_socket)
            other_socket.connections.append(self)

            # Execute connection functionality if both sockets have associated code
            if source_socket.associated_code and target_socket.associated_code:
                try:
                    # Extract the key for input socket (assuming it follows the pattern)
                    key = source_socket.associated_code.replace('[1]', '[-1]')
                    
                    # Call the connection functionality
                    # Note: This assumes a global 'functionality' object with a 'connect' method
                    functionality.connect(
                        _out=source_socket.associated_code, 
                        _in=target_socket.associated_code, 
                        key=key
                    )
                except Exception as e:
                    print(f"Connection functionality error: {e}")

    def disconnect(self, other_socket=None):
        """
        Disconnect this socket from all or a specific socket

        Args:
            other_socket (NodeSocket, optional): Specific socket to disconnect
        """
        if other_socket:
            if other_socket in self.connections:
                self.connections.remove(other_socket)
                other_socket.connections.remove(self)
        else:
            # Disconnect all connections
            for connection in self.connections[:]:
                self.disconnect(connection)

class BaseNode():
    def __init__(self, name, input_sockets=None, output_sockets=None):
        """
        Create a base node with configurable input and output sockets

        Args:
            name (str): Name of the node
            input_sockets (list, optional): List of input socket configurations
            output_sockets (list, optional): List of output socket configurations
        """
        self.name = name
        self.input_sockets = {}
        self.output_sockets = {}
        self.node_id = id(self)  # Add unique identifier

        # Store reference to this node in sockets
        def setup_socket(socket):
            socket.node = self
            return socket

        # Create input sockets
        if input_sockets:
            for socket_config in input_sockets:
                self.add_input_socket(**socket_config)

        # Create output sockets
        if output_sockets:
            for socket_config in output_sockets:
                self.add_output_socket(**socket_config)

    def add_input_socket(self, name, socket_type="any", associated_code=None):
        """
        Add an input socket to the node
        
        Args:
            name (str): Socket name
            socket_type (str): Socket type
            associated_code (str, optional): Associated Maya code
            
        Returns:
            NodeSocket: Created socket
        """
        socket = NodeSocket(name, socket_type, is_input=True, associated_code=associated_code)
        socket.node = self
        self.input_sockets[name] = socket
        return socket

    def add_output_socket(self, name, socket_type="any", associated_code=None):
        """
        Add an output socket to the node
        
        Args:
            name (str): Socket name
            socket_type (str): Socket type
            associated_code (str, optional): Associated Maya code
            
        Returns:
            NodeSocket: Created socket
        """
        socket = NodeSocket(name, socket_type, is_input=False, associated_code=associated_code)
        socket.node = self
        self.output_sockets[name] = socket
        return socket




###### Modules ######

class Control(BaseNode):
    def __init__(self, name):
        super().__init__(
            name,
            input_sockets=[
                {"name": "scale_in", "socket_type": "any", "associated_code": "connectionsControl[0]"},
                {"name": "controlFK_in", "socket_type": "any", "associated_code": "connectionsControl[1]"}
            ],
            output_sockets=[
                {"name": "control_out", "socket_type": "any", "associated_code": "connectionsControl[2]"}
            ]
        )
        

        # Default params
        self.controlShape = "circle"
        self.controlName = "Control"
        self.identifier = self.controlName + "_" + name
        self.lineWidth = 2
        self.controlColour = "red"

        # Create a proxy widget for controls
        self.controlWidget = QtWidgets.QWidget()
        self.controlLayout = QtWidgets.QVBoxLayout(self.controlWidget)

        # Create control shape selection
        self.controlShapeLabel = QtWidgets.QLabel("Control Shape:")
        self.controlShapeCombo = QtWidgets.QComboBox()
        self.controlShapeCombo.addItems(["circle", "arrow", "cube", "cylinder", "scapula", "square"])
        self.controlShapeCombo.setCurrentText(str(self.controlShape))
        self.controlShapeCombo.currentTextChanged.connect(self._update_control_shape)

         # Create control colour selection
        self.controlColourLabel = QtWidgets.QLabel("Control Colour:")
        self.controlColourCombo = QtWidgets.QComboBox()
        self.controlColourCombo.addItems(["red", "yellow", "blue", "orange", "light blue", "green"])
        self.controlColourCombo.setCurrentText(str(self.controlColour))
        self.controlColourCombo.currentTextChanged.connect(self._update_control_colour)

        # Create an image label for the control node
        self.image_label = QtWidgets.QLabel()
        self.image_label.setPixmap(QtGui.QPixmap(image_path + "control.png"))

        # Add widgets to layout
        self.controlLayout.addWidget(self.controlColourLabel)
        self.controlLayout.addWidget(self.controlColourCombo)
        self.controlLayout.addWidget(self.controlShapeLabel)
        self.controlLayout.addWidget(self.controlShapeCombo)
        self.controlLayout.addWidget(self.image_label)


    def _update_control_shape(self, value):
        """Update the control shape"""
        self.controlShape = str(value)

    def _update_control_colour(self, value):
        """Update the control colour"""
        self.controlColour = str(value)

class TwoBoneIK(BaseNode):
    def __init__(self, name):
        super().__init__(
            name,
            input_sockets=[
                {"name": "scale_in", "socket_type": "any", "associated_code": "connectionsIKarms[0]"},
                {"name": "shoulderIK_in", "socket_type": "any", "associated_code": "connectionsIKarms[1]"},
                {"name": "poleVectorIK_in", "socket_type": "any", "associated_code": "connectionsIKarms[2]"},
                {"name": "shoulderFK_in", "socket_type": "any", "associated_code": "connectionsIKarms[3]"}
            ],
            output_sockets=[
                {"name": "wrist_out", "socket_type": "any", "associated_code": "connectionsIKarms[4]"}
            ]
        )

        # Add default parameters
        self.twistJoints = "0"
        self.addon = "None"

        # Create a proxy widget for twist joints
        self.controlWidget = QtWidgets.QWidget()
        self.controlLayout = QtWidgets.QVBoxLayout(self.controlWidget)
        
        # Create control joints selection
        self.twistJointsLabel = QtWidgets.QLabel("Twist Joints:")
        self.twistJointsCombo = QtWidgets.QComboBox()
        self.twistJointsCombo.addItems(["0", "1", "2", "3"])
        self.twistJointsCombo.setCurrentText(str(self.twistJoints))
        self.twistJointsCombo.currentTextChanged.connect(self._update_twist_joints)

         # Create addon selection
        self.addonLabel = QtWidgets.QLabel("Add-ons:")
        self.addonCombo = QtWidgets.QComboBox()
        self.addonCombo.addItems(["None", "SquashAndStretch"])
        self.addonCombo.setCurrentText(str(self.addon))
        self.addonCombo.currentTextChanged.connect(self._update_addon)

        # Create an image label for the control node
        self.image_label = QtWidgets.QLabel()
        self.image_label.setPixmap(QtGui.QPixmap(image_path + "armik.png"))

        # Add widgets to layout
        self.controlLayout.addWidget(self.twistJointsLabel)
        self.controlLayout.addWidget(self.twistJointsCombo)
        self.controlLayout.addWidget(self.addonLabel)
        self.controlLayout.addWidget(self.addonCombo)
        self.controlLayout.addWidget(self.image_label)

    def _update_twist_joints(self, value):
        """Update the number of twist joints"""
        self.twistJoints = int(value)

    def _update_addon(self, value):
        """Update the addon selection"""
        self.addon = str(value)

class splineSpineIK(BaseNode):
    def __init__(self, name):
        super().__init__(
            name,
            input_sockets=[
                {"name": "scale_in", "socket_type": "any", "associated_code": "connectionsSpineIK[0]"}
            ],
            output_sockets=[
                {"name": "pelvis_out", "socket_type": "vector", "associated_code": "connectionsSpineIK[1]"},
                {"name": "spineTop_out", "socket_type": "vector", "associated_code": "connectionsSpineIK[2]"}
            ]
        )

        # Add default parameters
        self.numControlJoints = 3
        self.numJoints = 5
        self.addon = "None"

        # Create a proxy widget for controls
        self.controlWidget = QtWidgets.QWidget()
        self.controlLayout = QtWidgets.QVBoxLayout(self.controlWidget)
        
        # Create control joints selection
        self.controlJointsLabel = QtWidgets.QLabel("Control Joints:")
        self.controlJointsCombo = QtWidgets.QComboBox()
        self.controlJointsCombo.addItems(["2", "3", "4", "5"])
        self.controlJointsCombo.setCurrentText(str(self.numControlJoints))
        self.controlJointsCombo.currentTextChanged.connect(self._update_control_joints)
        
        # Create number of joints input
        self.jointsLabel = QtWidgets.QLabel("Number of Joints:")
        self.jointsSpinBox = QtWidgets.QSpinBox()
        self.jointsSpinBox.setMinimum(2)
        self.jointsSpinBox.setMaximum(999)
        self.jointsSpinBox.setValue(self.numJoints)
        self.jointsSpinBox.valueChanged.connect(self._update_joints)

        # Create addon selection
        self.addonLabel = QtWidgets.QLabel("Add-ons:")
        self.addonCombo = QtWidgets.QComboBox()
        self.addonCombo.addItems(["None", "SquashAndStretch"])
        self.addonCombo.setCurrentText(str(self.addon))
        self.addonCombo.currentTextChanged.connect(self._update_addon)

        # Create an image label for the splineSpineIK node
        self.image_label = QtWidgets.QLabel()
        self.image_label.setPixmap(QtGui.QPixmap(image_path + "spinesplineik.png"))
        
        # Add widgets to layout
        self.controlLayout.addWidget(self.controlJointsLabel)
        self.controlLayout.addWidget(self.controlJointsCombo)
        self.controlLayout.addWidget(self.jointsLabel)
        self.controlLayout.addWidget(self.jointsSpinBox)
        self.controlLayout.addWidget(self.addonLabel)
        self.controlLayout.addWidget(self.addonCombo)
        self.controlLayout.addWidget(self.image_label)
        
        
    def _update_control_joints(self, value):
        """Update the number of control joints"""
        self.numControlJoints = int(value)
        
    def _update_joints(self, value):
        """Update the number of joints"""
        self.numJoints = value

    def _update_addon(self, value):
        """Update the addon selection"""
        self.addon = str(value)


class FKChain(BaseNode):
    def __init__(self, name):
        super().__init__(
            name,
            input_sockets=[
                {"name": "scale_in", "socket_type": "any", "associated_code": "connectionsFKChain[0]"},
                {"name": "FKChain_in", "socket_type": "any", "associated_code": "connectionsFKChain[1]"}
            ],
            output_sockets=[
                {"name": "FKChain_out", "socket_type": "vector", "associated_code": "connectionsFKChain[2]"},
            ]
        )

        # Add default parameters
        self.numJoints = 3
        self.controlShape = "circle"
        self.controlName = "Control"
        self.identifier = self.controlName + "_" + name
        self.lineWidth = 2
        self.controlColour = "red"

        # Create a proxy widget for controls
        self.controlWidget = QtWidgets.QWidget()
        self.controlLayout = QtWidgets.QVBoxLayout(self.controlWidget)
        
        # Create control joints selection
        self.jointsLabel = QtWidgets.QLabel("Joints:")
        self.jointsCombo = QtWidgets.QComboBox()
        self.jointsCombo.addItems(["2", "3", "4", "5"])
        self.jointsCombo.setCurrentText(str(self.numJoints))
        self.jointsCombo.currentTextChanged.connect(self._update_joints)

        # Create control shape selection
        self.controlShapeLabel = QtWidgets.QLabel("Control Shape:")
        self.controlShapeCombo = QtWidgets.QComboBox()
        self.controlShapeCombo.addItems(["circle", "arrow", "cube", "cylinder", "scapula", "square"])
        self.controlShapeCombo.setCurrentText(str(self.controlShape))
        self.controlShapeCombo.currentTextChanged.connect(self._update_control_shape)

         # Create control colour selection
        self.controlColourLabel = QtWidgets.QLabel("Control Colour:")
        self.controlColourCombo = QtWidgets.QComboBox()
        self.controlColourCombo.addItems(["red", "yellow", "blue", "orange", "light blue", "green"])
        self.controlColourCombo.setCurrentText(str(self.controlColour))
        self.controlColourCombo.currentTextChanged.connect(self._update_control_colour)

        # Create an image label for the control node
        self.image_label = QtWidgets.QLabel()
        self.image_label.setPixmap(QtGui.QPixmap(image_path + "fkchain.png"))
        
        # Add widgets to layout
        self.controlLayout.addWidget(self.jointsLabel)
        self.controlLayout.addWidget(self.jointsCombo)
        self.controlLayout.addWidget(self.controlColourLabel)
        self.controlLayout.addWidget(self.controlColourCombo)
        self.controlLayout.addWidget(self.controlShapeLabel)
        self.controlLayout.addWidget(self.controlShapeCombo)
        self.controlLayout.addWidget(self.image_label)
        
    def _update_joints(self, value):
        """Update the number of control joints"""
        self.numJoints = int(value)

    def _update_control_shape(self, value):
        """Update the control shape"""
        self.controlShape = str(value)

    def _update_control_colour(self, value):
        """Update the control colour"""
        self.controlColour = str(value)


class foot(BaseNode):
    def __init__(self, name):
        super().__init__(
            name,
            input_sockets=[
                {"name": "scale_in", "socket_type": "any", "associated_code": "connectionsfoot[0]"},
                {"name": "ankle_in", "socket_type": "any", "associated_code": "connectionsfoot[1]"},
                {"name": "ball_in", "socket_type": "any", "associated_code": "connectionsfoot[2]"},
                {"name": "toe_in", "socket_type": "any", "associated_code": "connectionsfoot[3]"}
            ],
            output_sockets=[
                {"name": "toe_out", "socket_type": "any", "associated_code": "connectionsfoot[4]"}
            ]
        )

        # Add default parameters
        self.addon = "None"

        # Create a proxy widget for twist joints
        self.controlWidget = QtWidgets.QWidget()
        self.controlLayout = QtWidgets.QVBoxLayout(self.controlWidget)

         # Create addon selection
        self.addonLabel = QtWidgets.QLabel("Add-ons:")
        self.addonCombo = QtWidgets.QComboBox()
        self.addonCombo.addItems(["None", "SquashAndStretch"])
        self.addonCombo.setCurrentText(str(self.addon))
        self.addonCombo.currentTextChanged.connect(self._update_addon)

        # Create an image label for the control node
        self.image_label = QtWidgets.QLabel()
        self.image_label.setPixmap(QtGui.QPixmap(image_path + "foot.png"))

        # Add widgets to layout
        self.controlLayout.addWidget(self.addonLabel)
        self.controlLayout.addWidget(self.addonCombo)
        self.controlLayout.addWidget(self.image_label)

    def _update_addon(self, value):
        """Update the addon selection"""
        self.addon = str(value)
        


###### Add-Ons ######

class SquashAndStretch(BaseNode):
    def __init__(self, name):
        super().__init__(
            name,
            input_sockets=[
                {"name": "temp_in", "socket_type": "any", "associated_code": "temp[0]"}
            ],
            output_sockets=[
                {"name": "squash_and_stretch_out", "socket_type": "any", "associated_code": "temp[0]"}
            ]
        )
