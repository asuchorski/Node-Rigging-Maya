import sys
import os
import importlib
import maya.cmds as cmds # type: ignore

# Absolute path to the script modules
script_path = r"C:\\Users\\Asuch\\Desktop\\RiggingTool"

if script_path not in sys.path:
    sys.path.append(script_path)

# Reload py files uesd by modules
import functionality
importlib.reload(functionality)

import storeObjectsInJSON
importlib.reload(storeObjectsInJSON)

## Create Base Groups If They Dont Exist ##
if not cmds.objExists("RIG_TEMP_GRP_ALL"):
    cmds.select(clear=True)
    cmds.group(empty=True, name="RIG_TEMP_GRP_ALL")
    
if not cmds.objExists("RIG_GRP_ALL"):
    cmds.select(clear=True)
    cmds.group(empty=True, name="RIG_GRP_ALL")


### Create Modules Here ###
### Change identifier to uniquely identify each rig block ###
### Create a variable for each block as they return connections you can input and output ###

#import IKarms
#importlib.reload(IKarms)
#IKarms.template(identifier="NULL")
#connectionsIKarms = IKarms.twoBoneIK(identifier="NULL")

#import splineSpineIK
#importlib.reload(splineSpineIK)
#splineSpineIK.template(identifier = "NULL", numControlJoints=3)
#connectionsSpineIK = splineSpineIK.splineSpineIK(identifier= "NULL", numControlJoints=3, numJoints=5)

import Control
importlib.reload(Control)
Control.template(identifier = "NULL")
connectionsControl = Control.Control(control = "circle", identifier= "NULL")





### Prototype for making and deleting connections ###

#connection1 = functionality.connect(_out = connectionsSpineIK[2], _in = connectionsIKarms[1], key = connectionsIKarms[-1])
#connection2 = functionality.connect(_out = connectionsSpineIK[2], _in = connectionsIKarms[3], key = connectionsIKarms[-1])
#connection3 = functionality.connect(_out = connectionsSpineIK[2], _in = connectionsIKarms[2], key = connectionsIKarms[-1])

#functionality.disconnect(connection=connection1)
#functionality.disconnect(connection=connection2)
#functionality.disconnect(connection=connection3)