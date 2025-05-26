import maya.cmds as cmds  # type: ignore
from addon_SquashAndStretch import addon_SquashAndStretch
from functionality import importer, templateImporter, createOffsetGrp, matchTransform, createGroup, createJoints, constraintJointChains, createFKControls, setupIKFKSwitch, setupIKFKVisibility, lockAttributes
from storeObjectsInJSON import loadGeneratedObjects, cleanSpecificList, addObjectToList

generatedObjects = loadGeneratedObjects()  # Load existing data from JSON file at the start

def template(identifier = "NULL"):
    key = "FTTEMP_" + identifier
    cleanSpecificList(key)
    print(key)
    templateImporter("Scenes\\Templates\\foot.ma", key)

# Creates a foot setup
def foot(addon = "NULL", identifier = "NULL"):
    cmds.select(clear=True)

    # Define the key that will be used in every object created by the code to identifiy it
    key = "FT_" + identifier
    tempKey = "FTTEMP_" + identifier

    revLocators = ["heel_LOC_" + tempKey, "toe_LOC_" + tempKey, "ball_LOC_" + tempKey, "ankle_LOC_" + tempKey]
    locators = ["ankle_LOC_" + tempKey, "ball_LOC_" + tempKey, "toe_LOC_" + tempKey]
    ikJointNames = ["ankle_IK_" + key + "_JNT", "ball_IK_" + key + "_JNT", "toe_IK_" + key + "_JNT"]
    fkJointNames = ["ankle_FK_" + key + "_JNT", "ball_FK_" + key + "_JNT", "toe_FK_" + key + "_JNT"]
    revJointNames = ["heel_REV_" + key + "_JNT", "toe_REV_" + key + "_JNT", "ball_REV_" + key + "_JNT", "ankle_REV_" + key + "_JNT"]
    envJointNames = ["ankle_ENV_" + key + "_JNT", "ball_ENV_" + key + "_JNT", "toe_ENV_" + key + "_JNT"]

    ikJoints = []
    fkJoints = []
    envJoints = []
    revJoints = []
    revLocatorPositions = {}
    locatorPositions = {}

    cleanSpecificList(key)  # Clean any existing objects in the 'foot' list

    # IK Joints
    jointsIK = createJoints(jointNames=ikJointNames, joints=ikJoints, locators=locators, locatorPositions=locatorPositions, key=key)[0]
    # FK Joints
    jointsFK = createJoints(jointNames=fkJointNames, joints=fkJoints, locators=locators, locatorPositions=locatorPositions, key=key)[0]
    # ENV Joints
    envJoitns = createJoints(jointNames=envJointNames, joints=envJoints, locators=locators, locatorPositions=locatorPositions, key=key)[0]
    # REV Joints
    revJoitns = createJoints(jointNames=revJointNames, joints=revJoints, locators=revLocators, locatorPositions=revLocatorPositions, key=key)[0]


    # Create point and orient constraints between ik, fk and env joints
    constraintJointChains(rootJntOne=ikJoints[0], rootJntTwo=envJoints[0], key=key)
    constraintJointChains(rootJntOne=fkJoints[0], rootJntTwo=envJoints[0], key=key)

    # Function to create fk controls and position them
    fkControls,fkControlOffsetGrps = createFKControls(control="Scenes\\circle.ma", fkChain=fkJoints, key=key)

    switchControl = importer(item="Scenes\\arrow.ma", name="Foot_Settings_" + key, key=key, scale = [0.25, 0.25, 0.25], lineWidth=2.0, colour=6)
    setupIKFKSwitch(envChain=envJoints, fkChain=fkJoints, ikChain=ikJoints, switchCtrl=switchControl, key=key )
    switchOffsetGrp = createOffsetGrp(item=switchControl, key=key)
    matchTransform(source=switchOffsetGrp, target=locators[0], transOffset=[4,0,0], rotOffset=[90,0,90])

    # Create IK foot control and move it into place
    footControl = importer(item="Scenes\\cube.ma", name="Foot_CTRL_" + key , key=key, colour=17)
    ballPos = locatorPositions.get("ball_LOC_" + tempKey)
    cmds.xform(footControl, worldSpace=True, translation=ballPos)
    cmds.makeIdentity(footControl, apply=True, translate=True, rotate=True, scale=True, normal=False)
    footControlOffsetGrp = createOffsetGrp(footControl, key)
