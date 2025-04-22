import maya.cmds as cmds  # type: ignore
from functionality import importer, templateImporter, createOffsetGrp, matchTransform, createGroup, createJoints, constraintJointChains, createFKControls, setSelectedControlsColorAndLineWidth
from storeObjectsInJSON import loadGeneratedObjects, cleanSpecificList, addObjectToList

generatedObjects = loadGeneratedObjects()  # Load existing data from JSON file at the start

def addon_SquashAndStretch(ikChain, fkChain, envChain, switch, ikCurve , scaleAxis, identifier):
    cmds.select(clear=True)

    key = "addon_SquashAndStretch_" + identifier 
    cleanSpecificList(key)  # Clean any existing objects in the 'SquashAndStretch' list

    # Define the expected shape name
    curveShape = ikCurve + "Shape"

    # Create the curveInfo node
    curveInfo = cmds.createNode('curveInfo', name=f'{curveShape}_curveInfo' + key)
    addObjectToList(key, curveInfo)

    # Connect worldSpace[0] of shape to inputCurve of curveInfo
    cmds.connectAttr(f'{curveShape}.worldSpace[0]', f'{curveInfo}.inputCurve', force=True)
    
    # Create the multiply/divide node
    multiplyDivideNode = cmds.createNode('multiplyDivide', name=f'{curveShape}_multiplyDivide_{key}')
    addObjectToList(key, multiplyDivideNode)
    
    # Set the operation to divide
    cmds.setAttr(f"{multiplyDivideNode}.operation", 2)  # 2 = divide
    
    # Connect the arc length output to the input 1X of the multiply/divide node
    cmds.connectAttr(f"{curveInfo}.arcLength", f"{multiplyDivideNode}.input1X", force=True)
    
    # Get the actual arc length value and plug it into the input 2X of the multiply/divide node
    arcLength = cmds.getAttr(f"{curveInfo}.arcLength")
    cmds.setAttr(f"{multiplyDivideNode}.input2X", arcLength)


    # Remove first and last element from joint list (Dont scale pelvis and neck as this will affect head and legs)
    ikChain = ikChain[1:-1]
    envChain = envChain[1:-1]
    

    # Loop through the ikChain and connect the output X from the multiplyDivide node
    # to the Scale Y of each of the joints in the ikChain
    for joint in ikChain:
        try:
            cmds.setAttr('%s.segmentScaleCompensate'%(joint),1)
            if scaleAxis == "Y":
                cmds.connectAttr(f"{multiplyDivideNode}.outputX", f"{joint}.scaleY", force=True)
            if scaleAxis == "X":
                cmds.connectAttr(f"{multiplyDivideNode}.outputX", f"{joint}.scaleX", force=True)

        except Exception as e:
            print(f"Skipping {joint} due to error: {e}")
            continue

    # Create inverse multiply divide node and inverse the arc length
    multiplyDivideNodeInverse = cmds.createNode('multiplyDivide', name=f'{curveShape}_multiplyDivideInverse_{key}')
    addObjectToList(key, multiplyDivideNodeInverse)
    # Set the operation to power
    cmds.setAttr(f"{multiplyDivideNodeInverse}.operation", 3)  # 2 = power
    cmds.setAttr(f"{multiplyDivideNodeInverse}.input2X", -1)
    cmds.connectAttr(f"{multiplyDivideNode}.outputX", f"{multiplyDivideNodeInverse}.input1X", force=True)


    # Connect enc chains x and z scale values to squash and stretch with the curve
    for joint in envChain:
        try:
            cmds.setAttr('%s.segmentScaleCompensate'%(joint),1)
            if scaleAxis == "Y":
                cmds.connectAttr(f"{multiplyDivideNodeInverse}.outputX", f"{joint}.scaleX", force=True)
            if scaleAxis == "X":
                cmds.connectAttr(f"{multiplyDivideNodeInverse}.outputX", f"{joint}.scaleY", force=True)
            cmds.connectAttr(f"{multiplyDivideNodeInverse}.outputX", f"{joint}.scaleZ", force=True)

        except Exception as e:
            print(f"Skipping {joint} due to error: {e}")
            continue


    return curveInfo, multiplyDivideNode, multiplyDivideNodeInverse
