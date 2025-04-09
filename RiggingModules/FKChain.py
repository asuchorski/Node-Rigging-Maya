import maya.cmds as cmds  # type: ignore
from functionality import importer, templateImporter, createOffsetGrp, matchTransform, createGroup, createJoints, constraintJointChains, createFKControls, setSelectedControlsColorAndLineWidth, subdivideJointChain
from storeObjectsInJSON import loadGeneratedObjects, cleanSpecificList, addObjectToList

generatedObjects = loadGeneratedObjects()  # Load existing data from JSON file at the start

def template(numJoints=3, identifier="NULL"):
    key = "FKCHNTEMP" + str(numJoints) + "_" + identifier
    cleanSpecificList(key)
    templateImporter("Scenes\\Templates\\FKChain" + "_0" + str(numJoints) +".ma", key)

# Creates a two bone IK setup
def FKChain(Control, Colour, numJoints, identifier = "NULL"):
    cmds.select(clear=True)
    tempKey = "FKCHNTEMP"
    # Adding the numControls at the end to determine the correct group to look through
    TEMPGroupName = f"FKChain_TEMPLATE_0{numJoints}" + "_" + tempKey +  str(numJoints) + "_" + identifier
    locators = []

    # Get locators from imported template and add them to the locator list
    children = cmds.listRelatives(TEMPGroupName, children=True, fullPath=True) or []
    for child in children:
        shapes = cmds.listRelatives(child, shapes=True, fullPath=True) or []
        if shapes:  # Ensures it's not a group
            for shape in shapes:
                if cmds.objectType(shape) == "locator":
                    short_name = cmds.ls(child, shortNames=True)[0]  # Get the short name
                    locators.append(short_name)
    
    # Define the key that will be used in every object created by the code to identifiy it
    key = "FKCHN" + str(numJoints) + "_" + identifier
    
    FKJointNames = []
    ENVJointNames = []

    # loop though locators to create control joints and rename
    for loc in locators:
        nameReplace = loc.replace("LOC", "FK_JNT")  # Replace "LOC" with "JNT"
        newName = nameReplace
        FKJointNames.append(newName)

        nameReplace = loc.replace("LOC", "ENV_JNT")  # Replace "LOC" with "JNT"
        newName = nameReplace
        ENVJointNames.append(newName)

    # Set up IK FK and ENV joints
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

    print(colourIndex)

     # Function to create fk controls and position them
    controlShape= "Scenes\\" + Control + ".ma"

    print (controlShape)

    # Clean JSON file and scene before running script
    cleanSpecificList(key)

    # FK joint chain
    fkJoints, locatorPositions = createJoints(jointNames=FKJointNames, joints=fkJoints, locators=locators, locatorPositions=locatorPositions, key=key, radius=3, parent=True)

    # ENV joint chain
    envJoints, locatorPositions = createJoints(jointNames=ENVJointNames, joints=envJoints, locators=locators, locatorPositions=locatorPositions, key=key, radius=3, parent=True)

    # Create point and orientconstraints between ik, fk and env joints
    constraintJointChains(rootJntOne=fkJoints[0], rootJntTwo=envJoints[0], key=key)

    # FK Controls
    fkControls,fkControlOffsetGrps = createFKControls(control= controlShape, fkChain=fkJoints, key=key)

    # Colour Control
    setSelectedControlsColorAndLineWidth(colorIndex=colourIndex, importedControl=fkControls, lineWidth=2)

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

    # Ins and Outs
    ### Outs: Are like drivers, they control what happens to the inputs
    ### Ins: Are like the driven, they are being controlled by the outputs

    FKChain_in = fkControlOffsetGrps[0]
    scale_in = controlGrp

    FKChain_out = envJoints[-1]

    return scale_in, FKChain_in, FKChain_out, key




    