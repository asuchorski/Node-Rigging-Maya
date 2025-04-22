import sys
import os
import importlib

# Add the script path to UI BEFORE importing
script_path = r"C:\\Users\\Asuch\\Desktop\\RiggingTool\\NodeEditorUI"
if script_path not in sys.path:
    sys.path.append(script_path)

# Reload node UI modules
import node_editor_ui
importlib.reload(node_editor_ui)
import node_editor
importlib.reload(node_editor)
import node_item
importlib.reload(node_item)
import node_addon
importlib.reload(node_addon)
import node_navigation
importlib.reload(node_navigation)
import node_node
importlib.reload(node_node)
import node_graphics
importlib.reload(node_graphics)
import node_context_menu
importlib.reload(node_context_menu)
import node_main_menu
importlib.reload(node_main_menu)
import node_serialization
importlib.reload(node_serialization)
import node_data_manager
importlib.reload(node_data_manager)

# Add the script path to rigging modules BEFORE importing
script_path = r"C:\\Users\\Asuch\\Desktop\\RiggingTool\\RiggingModules"
if script_path not in sys.path:
    sys.path.append(script_path)

# Reload py files uesd by rigging modules
import functionality
importlib.reload(functionality)
import storeObjectsInJSON
importlib.reload(storeObjectsInJSON)
import IKarms
importlib.reload(IKarms)
import splineSpineIK
importlib.reload(splineSpineIK)
import Control
importlib.reload(Control)
import FKChain
importlib.reload(FKChain)


from node_editor_ui import show_node_editor
show_node_editor()

