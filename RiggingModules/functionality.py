import maya.cmds as cmds # type: ignore
import os
from storeObjectsInJSON import loadGeneratedObjects, cleanSpecificList, addObjectToList
import math

USER_SCENE_PATH = "C:\\Users\\Asuch\\Desktop\\RiggingTool"

# Custom control colour and line width are set using next 4 functions
def setSelectedControlsColorAndLineWidth(colorIndex, lineWidth, importedControl):
    """Set the color and line width of the imported control."""
    if not importedControl:
        cmds.warning("No valid control provided for color and line width adjustment.")
        return
    
    # Ensure we process only a single control
    controls = [importedControl] if isinstance(importedControl, str) else importedControl
    
    for control in controls:
        if cmds.objectType(control) == "transform":
            shape_nodes = cmds.listRelatives(control, shapes=True, fullPath=True) or []
            for shape_node in shape_nodes:
                enable_color_override(shape_node)
                set_control_color(shape_node, colorIndex)
                set_control_line_width(shape_node, lineWidth)
        else:
            enable_color_override(control)
            set_control_color(control, colorIndex)
            set_control_line_width(control, lineWidth)

def enable_color_override(control):
    """Enable the color override for a specific control."""
    try:
        cmds.setAttr(f"{control}.overrideEnabled", 1)
    except RuntimeError as e:
        cmds.warning(f"Failed to enable color override for {control}: {e}")

def set_control_color(control, colorIndex):
    """Set the color override for a specific control."""
    try:
        cmds.setAttr(f"{control}.overrideColor", colorIndex)
    except RuntimeError as e:
        cmds.warning(f"Failed to set color for {control}: {e}")

def set_control_line_width(control, lineWidth):
    """Set the line width for a specific control."""
    try:
        cmds.setAttr(f"{control}.lineWidth", lineWidth)
    except RuntimeError as e:
        cmds.warning(f"Failed to set line width for {control}: {e}")

# Imports a control from external file given the control name
def importer(item, name, key, scale = [1,1,1], lineWidth=1.5, colour=5):
    """Import an external item from a file and apply a color and line width to it."""
    wholePath = os.path.join(USER_SCENE_PATH, item)
    
    importedNodes = cmds.file(wholePath, i=True, type="mayaAscii", mergeNamespacesOnClash=False, returnNewNodes=True)

    # Find the first transform node in the imported nodes
    importedTransform = next((node for node in importedNodes if cmds.objectType(node) == "transform"), None)

    if not importedTransform:
        cmds.warning("No transform node found in the imported file.")
        return None

    renamedItem = cmds.rename(importedTransform, name)

    # Apply color and line width settings to the imported control
    setSelectedControlsColorAndLineWidth(colour, lineWidth, renamedItem)
    cmds.scale(scale[0], scale[1], scale[2], renamedItem)

    addObjectToList(key, renamedItem)
    
    return renamedItem

# Creates an offset group for a given item
def createOffsetGrp(item, key):
    offsetGroup = cmds.group(empty=True, name=item + '_OffsetGrp')
    cmds.parent(item, offsetGroup)

    # Zero out the group's transformations to match the control's current transform and pivots
    cmds.setAttr(offsetGroup + ".translate", 0, 0, 0)
    cmds.setAttr(offsetGroup + ".rotate", 0, 0, 0)
    cmds.setAttr(offsetGroup + ".scale", 1, 1, 1)
    control_pivot_translation = cmds.xform(item, query=True, rotatePivot=True, worldSpace=True)
    cmds.xform(offsetGroup, worldSpace=True, pivots=control_pivot_translation)
    addObjectToList(key, offsetGroup)

    return offsetGroup

# Creates a standard group for a given item
def createGroup(name, key):
    group = cmds.group(empty=True, name=name + "_" + key + '_Grp')
    addObjectToList(key, group)

    return group

# Matches the transforms of the source to the target with an optional offset
def matchTransform(source, target, transOffset=[0, 0, 0], rotOffset=[0,0,0]):
    targetPos = cmds.xform(target, query=True, worldSpace=True, translation=True)
    targetRot = cmds.xform(target, query=True, worldSpace=True, rotation=True)
    
    # Apply the offset
    newPos = [targetPos[0] + transOffset[0], targetPos[1] + transOffset[1], targetPos[2] + transOffset[2]]
    newRot = [targetRot[0] + rotOffset[0], targetRot[1] + rotOffset[1], targetRot[2] + rotOffset[2]]

    cmds.xform(source, worldSpace=True, translation=newPos, rotation=newRot)
    cmds.makeIdentity(source, apply=True, translate=True, rotate=True, scale=True, normal=False)

# Imports the template for a rig module for the user to position
def templateImporter(item, key):
    newNodes = []
    wholePath = os.path.join(USER_SCENE_PATH, item)
    
    # Import the file and get the imported nodes
    importedNodes = cmds.file(wholePath, i=True, type="mayaAscii", mergeNamespacesOnClash=False, returnNewNodes=True)

    baseNodeNames = [node.split('|')[-1] for node in importedNodes]

    # Loop through the file and rename each node adding the key suffix identifier
    for node in baseNodeNames:

        if node.endswith("Shape"):
            continue

        if node.endswith("Orig"):
            continue

        newName = node + "_" + key
        cmds.rename(node, newName)
        addObjectToList(key, newName)
        newNodes.append(newName)

    topGroups = [
    node for node in newNodes
    if cmds.objectType(node) == "transform" and not cmds.listRelatives(node, parent=True)
]

    if topGroups:
        topGroup = topGroups[0]  # Assuming only one topmost group exists
        print(f"Topmost group found: {topGroup}")
    else:
        print("No top-level group found.")

    cmds.parent(topGroups[0], "RIG_TEMP_GRP_ALL")

    return importedNodes

def scaleCompensate(joints):
    for j in joints:
        cmds.setAttr(f"{j}.segmentScaleCompensate", 0)

# Creates joints given a list of locators and a list of joint names. 
def createJoints(locators, jointNames, locatorPositions, joints, key, radius = 1, parent=True):
    cmds.select(clear=True)
    for loc, jnt in zip(locators, jointNames):
        pos = cmds.xform(loc, query=True, worldSpace=True, translation=True)
        locatorPositions[loc] = pos
        if parent == False:
            cmds.select(clear=True)
        jntCreated = cmds.joint(name=jnt, position=pos, radius=radius)
        joints.append(jntCreated)
        addObjectToList(key, jntCreated)

    scaleCompensate(joints)
    return joints, locatorPositions

# Creates point and orient contraints between two joint chains e.g when creating ik-fk switching
def constraintJointChains(rootJntOne, rootJntTwo, key):
    # Get all joints in both hierarchies
    joints1 = cmds.listRelatives(rootJntOne, allDescendents=True, type='joint', fullPath=True)
    joints2 = cmds.listRelatives(rootJntTwo, allDescendents=True, type='joint', fullPath=True)
    
    # Include the root joints themselves
    joints1 = [rootJntOne] + joints1 if joints1 else [rootJntOne]
    joints2 = [rootJntTwo] + joints2 if joints2 else [rootJntTwo]
    
    # Add point and orient constraints with maintain offset
    for j1, j2 in zip(joints1, joints2):
        pointConstraint = cmds.pointConstraint(j1, j2, maintainOffset=True)[0]
        orientConstraint = cmds.orientConstraint(j1, j2, maintainOffset=True)[0]
        addObjectToList(key, pointConstraint)
        addObjectToList(key, orientConstraint)

# Create FK control for each fk joint given a control name to import and an fk joint chain
def createFKControls(fkChain, control, key, transOffset=[0,0,0], rotOffset=[0,0,0], scaleOffset=[1,1,1], parent=True, offsetGrp=True, colour=18):

    previousControl = None
    fkControls = []
    fkControlOffsetGrps = []
    
    for i, joint in enumerate(fkChain):
        base_name = fkChain[i].removesuffix('_JNT')  # Removes "_JNT" if it exists
        controlName = base_name + '_CTRL'
        
        fkControl = importer(item=control, name=controlName, scale=scaleOffset, key=key, colour=colour)
        matchTransform(source=fkControl, target=fkChain[i])

        pushRotToOffsetMat(item=fkControl)
        if offsetGrp == True:
            fkControlOffsetGrp = createOffsetGrp(item=fkControl, key=key)
            fkControlOffsetGrps.append(fkControlOffsetGrp)

        else:
            fkControlOffsetGrp = fkControl
        cmds.rotate(rotOffset[0], rotOffset[1], rotOffset[2], fkControl)
        cmds.move(transOffset[0], transOffset[1], transOffset[2], fkControl)
        cmds.makeIdentity(fkControl, apply=True, translate=True, rotate=True, scale=True, normal=False)

        if parent == True:
            if previousControl:
                cmds.parent(fkControlOffsetGrp, previousControl)
        
        previousControl=fkControl
        
        parentConstraint = cmds.parentConstraint(fkControl, fkChain[i], maintainOffset=True)[0]
        addObjectToList(key, parentConstraint)
        fkControls.append(fkControl)
        lockAttributes(item=fkControl, scale = 1, hidden = 1)

    return fkControls, fkControlOffsetGrps

# Next 3 functions are used to push rotate values to parent offset matrix of a chosen item
def degrees_to_radians(degrees):
    return degrees * (math.pi / 180.0)

def euler_to_matrix(rotation):
    rx, ry, rz = map(degrees_to_radians, rotation)
    
    cx = math.cos(rx)
    sx = math.sin(rx)
    cy = math.cos(ry)
    sy = math.sin(ry)
    cz = math.cos(rz)
    sz = math.sin(rz)

    # Calculate the rotation matrix
    matrix = [
        [cy * cz, -cy * sz, sy, 0],
        [sx * sy * cz + cx * sz, cx * cz - sx * sy * sz, -sx * cy, 0],
        [-cx * sy * cz + sx * sz, sx * cz + cx * sy * sz, cx * cy, 0],
        [0, 0, 0, 1]
    ]
    
    return matrix

# Push rotate values to parent offset matrix of chosen item
def pushRotToOffsetMat(item): 
    obj = item
    
    # Get the rotation values of the object and multiply by -1
    rotation = [-val for val in cmds.getAttr(obj + '.rotate')[0]]
    
    # Convert the rotation values to a matrix
    rotation_matrix = euler_to_matrix(rotation)
    
    # Get the current parent offset matrix
    offset_matrix = cmds.getAttr(obj + '.offsetParentMatrix')
    
    # Create a new offset matrix with the rotation values
    new_matrix = list(offset_matrix)
    
    for i in range(3):
        for j in range(3):
            new_matrix[i*4 + j] = rotation_matrix[i][j]
    
    # Set the new offset matrix
    cmds.setAttr(obj + '.offsetParentMatrix', *new_matrix, type='matrix')
    
    # Freeze transformations
    cmds.makeIdentity(obj, apply=True, rotate=True)

# Sets up the IK-FK switching of chosen fk and ik chains
def setupIKFKSwitch(envChain, fkChain, ikChain, switchCtrl, key):
    # Add the IK/FK switching attribute if it doesn't exist
    if not cmds.attributeQuery('IKFK', node=switchCtrl, exists=True):
        cmds.addAttr(switchCtrl, longName='IKFK', attributeType='float', min=0, max=1, defaultValue=0)
        cmds.setAttr(switchCtrl + ".IKFK", keyable=True)

    # Loop through the envChain, ikChain, and fkChain
    for i, envJoint in enumerate(envChain):
        ikJoint = ikChain[i]
        fkJoint = fkChain[i]

        # Find the constraints on the env joint
        constraints = cmds.listRelatives(envJoint, type=["pointConstraint", "orientConstraint"]) or []

        for constraint in constraints:
            # Determine if it's a point or orient constraint
            constraintType = cmds.nodeType(constraint)

            # Get the weight attributes for the IK and FK
            ikWeightAttr = f"{constraint}.{ikJoint}W0"
            fkWeightAttr = f"{constraint}.{fkJoint}W1"

            # Create a blendColors node and a reverse node
            blendNode = cmds.shadingNode('blendColors', asUtility=True, name=f"blendColors_{envJoint}_{constraintType}" + "_" + key)
            reverseNode = cmds.shadingNode('reverse', asUtility=True, name=f"reverse_{envJoint}_{constraintType}" + "_" + key)
            addObjectToList(key, blendNode)
            addObjectToList(key, reverseNode)

            # Set color1R to 1 and color2R to 0 in the blendColors node
            cmds.setAttr(blendNode + ".color1R", 1)
            cmds.setAttr(blendNode + ".color2R", 0)

            # Connect the IKFK switch attribute to the blend attribute of the blendColors node
            cmds.connectAttr(switchCtrl + ".IKFK", blendNode + ".blender", force=True)

            # Connect outputR from blendColors node to inputX of reverse node
            cmds.connectAttr(blendNode + ".outputR", reverseNode + ".inputX", force=True)

            # Connect outputX from reverse node to the IK weight attribute
            cmds.connectAttr(reverseNode + ".outputX", ikWeightAttr, force=True)

            # Connect outputR from blendColors node to the FK weight attribute
            cmds.connectAttr(blendNode + ".outputR", fkWeightAttr, force=True)

# Takes the setup IK-FK switching module and setus up visibility of controls for clarity
def setupIKFKVisibility(fkControls, ikControls, switchCtrl, key):
    # Loop through FK controls and connect visibility to IKFK attribute
    for fkCtrl in fkControls:
        cmds.connectAttr(switchCtrl + ".IKFK", fkCtrl + ".visibility", force=True)

    # Loop through IK controls, create a reverse node, and connect it
    for ikCtrl in ikControls:
        reverseNode = cmds.shadingNode("reverse", asUtility=True, name=f"reverse_{ikCtrl}_vis_" + key)
        addObjectToList(key, reverseNode)

        cmds.connectAttr(switchCtrl + ".IKFK", reverseNode + ".inputX", force=True)
        cmds.connectAttr(reverseNode + ".outputX", ikCtrl + ".visibility", force=True)

# Locks chosen attributes on specified item
def lockAttributes(item, trans = 0, rot = 0, scale = 0, vis = 0, hidden = 0):
    if trans > 0:
        cmds.setAttr(f"{item}.translateX", lock=True, keyable=False)
        cmds.setAttr(f"{item}.translateY", lock=True, keyable=False)
        cmds.setAttr(f"{item}.translateZ", lock=True, keyable=False)
        if hidden > 0:
            cmds.setAttr(f"{item}.translateX", channelBox=False)
            cmds.setAttr(f"{item}.translateY", channelBox=False)
            cmds.setAttr(f"{item}.translateZ", channelBox=False)

    if rot > 0:
        cmds.setAttr(f"{item}.rotateX", lock=True, keyable=False)
        cmds.setAttr(f"{item}.rotateY", lock=True, keyable=False)
        cmds.setAttr(f"{item}.rotateZ", lock=True, keyable=False)
        if hidden > 0:
            cmds.setAttr(f"{item}.rotateX", channelBox=False)
            cmds.setAttr(f"{item}.rotateY", channelBox=False)
            cmds.setAttr(f"{item}.rotateZ", channelBox=False)

    if scale > 0:
        cmds.setAttr(f"{item}.scaleX", lock=True, keyable=False)
        cmds.setAttr(f"{item}.scaleY", lock=True, keyable=False)
        cmds.setAttr(f"{item}.scaleZ", lock=True, keyable=False)
        if hidden > 0:
            cmds.setAttr(f"{item}.scaleX", channelBox=False)
            cmds.setAttr(f"{item}.scaleY", channelBox=False)
            cmds.setAttr(f"{item}.scaleZ", channelBox=False)

    if vis > 0:
        cmds.setAttr(f"{item}.visibility", lock=True, keyable=False)
        if hidden > 0:
            cmds.setAttr(f"{item}.visibility", channelBox=False)

# Inserts evenly a given amount of joints between two joints given a root joint
def subdivideJointChain(tmpStartEndJoints, jointSubdiv, key, name="spine", nameFirstJoint="pelvis"):
    rootJointCopy = cmds.duplicate(tmpStartEndJoints, rc=True)

    rootJointCopy[0] = cmds.rename(rootJointCopy[0], "startJoint001_"+ key)
    rootJointCopy[1] = cmds.rename(rootJointCopy[1], "endJoint001_" + key)
    
    rootJoint = rootJointCopy
    joint_chain = cmds.listRelatives(rootJoint[0], allDescendents=True, type='joint')
    joint_chain.append(rootJoint[0])
    joint_chain.reverse()

    new_joints = []

    start_joint = rootJoint[0]
    end_joint = rootJoint[1]

    # Rename the first joint to "pelvis_JNT"
    pelvis_joint = cmds.rename(start_joint, nameFirstJoint +  "_" + key + "_JNT")
    new_joints.append(pelvis_joint)
    addObjectToList(key, pelvis_joint)

    # Get the world space positions of the start and end joints
    start_pos = cmds.xform(pelvis_joint, query=True, worldSpace=True, translation=True)
    end_pos = cmds.xform(end_joint, query=True, worldSpace=True, translation=True)
    cmds.select(pelvis_joint)

    # Calculate the positions for the new joints
    for j in range(1, jointSubdiv + 1):
        t = j / (jointSubdiv + 1)
        new_pos = [(1 - t) * start_pos[k] + t * end_pos[k] for k in range(3)]

        # Create a new joint at the calculated position
        new_joint = cmds.joint(position=new_pos)
        # Rename the new joint to "spine_0x_JNT"
        renamedJoint = cmds.rename(new_joint, name + "_" + key + f"_0{j}_JNT")
        new_joints.append(renamedJoint)
        addObjectToList(key, renamedJoint)

    # Reparent the end joint to the last new joint
    cmds.parent(end_joint, new_joints[-1])

    # Rename the last joint (previously endJoint) to "spine_0(x+1)_JNT"
    last_index = jointSubdiv + 1
    lastJoint = cmds.rename(end_joint, name + "_" + key + f"_0{last_index}_JNT")
    new_joints.append(lastJoint)
    scaleCompensate(new_joints)
    addObjectToList(key, lastJoint)

    return new_joints

# Snaps given joint chain to a curve
def snapJointsToCurve(jointChain, curve, key):
    # Get the total length of the curve
    curve_length = cmds.arclen(curve)
    
    # Calculate the step size, which is the distance between each joint along the curve
    step = curve_length / (float(len(jointChain))-1)
    jointNum = len(jointChain)

    # Snap each joint to the curve, spaced evenly
    for i in range(1, jointNum):
        joint = jointChain[i]
        param = step * i / curve_length
        # Get the position of the joint at the calculated parameter
        position = cmds.pointOnCurve(curve, parameter=param, position=True)
        cmds.xform(joint, worldSpace=True, translation=position)

        # Add the joint to the key tracking list
        addObjectToList(key, joint)

# Set up twist nodes given ik handle and controls
def addTwistToSpline(controls, ikHandle, key):
    multiplyNode = cmds.shadingNode("multiplyDivide", asUtility=True, name=f"multiplyDivide" + key)
    plusMinAvgNode = cmds.shadingNode("plusMinusAverage", asUtility=True, name=f"plusMinusAverage" + key)
    addObjectToList(key, multiplyNode)
    addObjectToList(key, plusMinAvgNode)

    cmds.setAttr(multiplyNode + ".input2X", -1)

    cmds.connectAttr(controls[0] + ".rotateY", multiplyNode + ".input1X", force=True)
    cmds.connectAttr(multiplyNode + ".outputX", plusMinAvgNode + ".input1D[0]", force=True)

    cmds.connectAttr(plusMinAvgNode + ".output1D", ikHandle + ".twist", force=True)
    cmds.connectAttr(controls[0] + ".rotateY", ikHandle + ".roll", force=True)

    cmds.connectAttr(controls[-1] + ".rotateY", plusMinAvgNode + ".input1D[1]", force=True)

    # Loop through the middle controls (skipping first and last)
    for i, ctrl in enumerate(controls[1:-1], start=2):  # Start x at 2
        input_attr = f"{plusMinAvgNode}.input1D[{i}]"
        rotate_attr = f"{ctrl}.rotateY"
        
        cmds.connectAttr(rotate_attr, input_attr, force=True)

# Creates splineIK given control joints, joint chain, and curve
def createSplineIK(controlJoints, jointChain, curveIK, key):
    # Duplicate the curve so the original remains unchanged
    duplicatedCurve = cmds.duplicate(curveIK, name=curveIK + "_IK_" + key)[0]
    addObjectToList(key, duplicatedCurve)
    # Create the spline IK handle
    ikHandle = cmds.ikHandle(
        name=jointChain[0] + "_splineIK_" + key,
        startJoint=jointChain[0],
        endEffector=jointChain[-1],
        solver="ikSplineSolver",
        createCurve=False,
        curve=duplicatedCurve
    )[0]
    # Bind the duplicated curve to the control joints
    cmds.select(controlJoints, duplicatedCurve)
    splineIKSpineSkinCluster = cmds.skinCluster(tsb=True, name=duplicatedCurve + "_skinCluster_" + key)[0]
    addObjectToList(key, splineIKSpineSkinCluster)

    return ikHandle, duplicatedCurve


# Creates a parent connection between the out and in
def connect(_out, _in, key):

    parentConstraint = cmds.parentConstraint(_out, _in, maintainOffset=True)[0]
    addObjectToList(key, parentConstraint)

    return parentConstraint

# clears the parent connection between the out and in
def disconnect(connection):
    cmds.delete(connection)