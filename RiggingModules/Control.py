import maya.cmds as cmds  # type: ignore
from functionality import importer, templateImporter, createOffsetGrp, matchTransform, createGroup, createJoints, constraintJointChains, createFKControls, setSelectedControlsColorAndLineWidth
from storeObjectsInJSON import loadGeneratedObjects, cleanSpecificList, addObjectToList

generatedObjects = loadGeneratedObjects()  # Load existing data from JSON file at the start

def template(identifier = "NULL"):
    key = "CTRLTEMP_" + identifier
    cleanSpecificList(key)
    templateImporter("Scenes\\Templates\\control.ma", key)

# Creates a two bone IK setup
def Control(Control, Colour, identifier = "NULL"):
    cmds.select(clear=True)

    # Define the key that will be used in every object created by the code to identifiy it
    key = "CTRL_" + identifier
    tempKey = "CTRLTEMP_" + identifier

    locators = ["control_LOC_" + tempKey]
    fkJointNames = ["control_FK_" + key + "_JNT"]
    envJointNames = ["control_ENV_" + key + "_JNT"]

    fkJoints = []
    envJoints = []
    locatorPositions = {}

    # Set the colour index
    colourIndex = 0
    if Colour == "red":
        colourIndex = 13
    if Colour == "blue":
        colourIndex = 6
    if Colour == "yellow":
        colourIndex = 17
    if Colour == "light blue":
        colourIndex = 18
    if Colour == "orange":
        colourIndex = 12
    if Colour == "green":
        colourIndex = 14


    cleanSpecificList(key)  # Clean any existing objects in the 'twoBoneIK' list

    # FK Joints
    createJoints(jointNames=fkJointNames, joints=fkJoints, locators=locators, locatorPositions=locatorPositions, key=key)
    # ENV Joints
    envJoitns = createJoints(jointNames=envJointNames, joints=envJoints, locators=locators, locatorPositions=locatorPositions, key=key)[0]

    # Create point and orientconstraints between ik, fk and env joints
    constraintJointChains(rootJntOne=fkJoints[0], rootJntTwo=envJoints[0], key=key)

    # Function to create fk controls and position them
    controlShape= "Scenes\\" + Control + ".ma"
    fkControls,fkControlOffsetGrps = createFKControls(control= controlShape, fkChain=fkJoints, key=key)

    # Colour Control
    setSelectedControlsColorAndLineWidth(colorIndex=colourIndex, importedControl=fkControls[0], lineWidth=2)

    # Final Clean-Ups: Group remaining items
    jointsGroup = createGroup("joints", key)
    cmds.parent(fkJoints[0], jointsGroup)
    cmds.parent(envJoints[0], jointsGroup)
    
    controlGroup = createGroup("controls", key)
    
    controlGrp = createGroup("Control_RIG", key)
    cmds.parent(controlGroup, controlGrp)
    cmds.parent(jointsGroup, controlGrp)

    fkControlGroup = createGroup(name="FK_CTRL_GRP", key=key)

    cmds.parent(fkControlOffsetGrps[0], fkControlGroup)

    cmds.parent(fkControlGroup, controlGroup)

    ## Parent to base groups ##

    cmds.parent(controlGrp, "RIG_GRP_ALL")
    cmds.hide("control_TEMPLATE_" + tempKey)

    # Ins and Outs
    ### Outs: Are like drivers, they control what happens to the inputs
    ### Ins: Are like the driven, they are being controlled by the outputs

    controlFK_in = fkControlOffsetGrps[0]
    scale_in = controlGrp

    control_out = envJoitns[-1]

    return scale_in, controlFK_in, control_out, key
