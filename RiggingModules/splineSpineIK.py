import maya.cmds as cmds # type: ignore

from addon_SquashAndStretch import addon_SquashAndStretch
from functionality import importer, templateImporter, createOffsetGrp, matchTransform, createGroup, createJoints, constraintJointChains, createFKControls, setupIKFKSwitch, setupIKFKVisibility, lockAttributes, subdivideJointChain, snapJointsToCurve, createSplineIK, addTwistToSpline
from storeObjectsInJSON import loadGeneratedObjects, cleanSpecificList, addObjectToList

generatedObjects = loadGeneratedObjects()  # Load existing data from JSON file at the start

def template(numControlJoints=3, identifier="NULL"):
    key = "SSIKTEMP" + str(numControlJoints) + "_" + identifier
    cleanSpecificList(key)
    templateImporter("Scenes\\Templates\\splineSpineIK" + "_0" + str(numControlJoints) +".ma", key)
    #cmds.parent(template[0], "RIG_TEMP_GRP_ALL")

def splineSpineIK(numControlJoints=3, identifier="NULL", numJoints = 5, addon = "NULL"):
    cmds.select(clear=True)
    tempKey = "SSIKTEMP"
    # Adding the numControls at the end to determine the correct group to look through
    TEMPGroupName = f"splineSpineIK_TEMPLATE_0{numControlJoints}" + "_" + tempKey +  str(numControlJoints) + "_" + identifier
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
    key = "SSIK" + str(numControlJoints) + "_" + identifier

    spineCurve = f"spineCurve_TEMP_0{numControlJoints}" + "_" + tempKey + str(numControlJoints) + "_" + identifier
    
    ctrlJointNames = []

    # loop though locators to create control joints and rename
    for loc in locators:
        nameReplace = loc.replace("LOC", "JNT")  # Replace "LOC" with "JNT"
        newName = nameReplace + key
        ctrlJointNames.append(newName)

    # Set up temporary start and end joints
    tmpJointNames = ["startJoint", "endJoint"]
    tmpJoints = []
    tmpLocators = [locators[0], locators[-1]]
    tmpLocatorPositions = {}

    # Set up IK FK and ENV joints
    ikJoints = []
    fkJoints = []
    envJoints = []
    ctrlJoints = []
    locatorPositions = {}

    # Clean JSON file and scene before running script
    cleanSpecificList(key)

    # Create start and end joitns
    createJoints(jointNames=tmpJointNames,joints=tmpJoints, locators=tmpLocators, locatorPositions=tmpLocatorPositions, key=key)

    # IK joint chain
    ikJoints = subdivideJointChain(tmpStartEndJoints=tmpJoints, jointSubdiv=numJoints, key=key, name="spine_IK", nameFirstJoint="pelvis_IK")
    snapJointsToCurve(curve=spineCurve, jointChain=ikJoints, key=key)

    # FK joint chain
    fkJoints = subdivideJointChain(tmpStartEndJoints=tmpJoints, jointSubdiv=numJoints, key=key, name = "spine_FK", nameFirstJoint="pelvis_FK")
    snapJointsToCurve(curve=spineCurve, jointChain=fkJoints, key=key)
    # ENV joint chain
    envJoints = subdivideJointChain(tmpStartEndJoints=tmpJoints, jointSubdiv=numJoints, key=key, name = "spine_ENV", nameFirstJoint="pelvis_ENV")
    snapJointsToCurve(curve=spineCurve, jointChain=fkJoints, key=key)
    snapJointsToCurve(curve=spineCurve, jointChain=envJoints, key=key)

    # Create FK spine contols
    fkControls, fkControlOffsetGrps = createFKControls(control="Scenes\\circle.ma", fkChain=fkJoints, rotOffset=[90,0,0],scaleOffset=[4,4,4], key=key)

    # Create control joints
    ctrlJoints, locatorPositions = createJoints(jointNames=ctrlJointNames, joints=ctrlJoints, locators=locators, locatorPositions=locatorPositions, key=key, radius=3, parent=False)
    
    # Create Spline IK
    ikHandle, duplicatedCurve = createSplineIK(controlJoints=ctrlJoints, curveIK=spineCurve, jointChain=ikJoints, key=key)

    ikControls = []
    ikCtrlGrp = createGroup(name="IK_CTRL_GRP", key=key)
    ikControls = createFKControls(control="Scenes\\cube.ma", fkChain=ctrlJoints, key=key, scaleOffset=[2,2,2], parent=False, offsetGrp = False, colour=17)[0]

    for control in ikControls:  # Loop through each control in the list
        offsetGrp = createOffsetGrp(item=control, key=key)  # Create offset group
        cmds.parent(offsetGrp, ikCtrlGrp)  # Parent it under IK_CTRL_GRP

    constraintJointChains(rootJntOne=ikJoints[0], rootJntTwo=envJoints[0], key=key)
    constraintJointChains(rootJntOne=fkJoints[0], rootJntTwo=envJoints[0], key=key)

    switchControl = importer(item="Scenes\\arrow.ma", name="Spine_Settings_" + key, key=key, scale = [0.25, 0.25, 0.25], lineWidth=2.0, colour=6)
    matchTransform(source=switchControl, target=locators[1], transOffset=[5,0,0], rotOffset=[90,0,90])
    switchControlOffsetGrp = createOffsetGrp(item=switchControl, key=key)
    setupIKFKSwitch(envChain=envJoints, fkChain=fkJoints, ikChain=ikJoints, key=key, switchCtrl=switchControl)

    setupIKFKVisibility(fkControls=fkControls, ikControls=ikControls, switchCtrl=switchControl, key=key)

    addTwistToSpline(controls=ikControls, ikHandle=ikHandle, key=key)

    # Clean-up: Group remaining items
    jointGrp = createGroup(name="joints", key=key)
    cmds.parent(ikJoints[0], jointGrp)
    cmds.parent(fkJoints[0], jointGrp)
    cmds.parent(envJoints[0], jointGrp)

    fkCtrlGrp = createGroup(name="FK_CTRL_GRP", key=key)
    cmds.parent(fkControlOffsetGrps[0], fkCtrlGrp)
    #cmds.parent("pelvis_FK_SSIK_CTRL_OffsetGrp", fkCtrlGrp)

    ctrlJointsGrp = createGroup(name="ctrlJoints", key=key)
    cmds.parent(ctrlJoints, ctrlJointsGrp)
    cmds.parent(ctrlJointsGrp, jointGrp)

    controlsGrp = createGroup(name="controls", key=key)
    cmds.parent(ikCtrlGrp, controlsGrp)
    cmds.parent(fkCtrlGrp, controlsGrp)
    cmds.parent(switchControlOffsetGrp, controlsGrp)

    splineSpineIKRigGrp = createGroup(name="splineSpineIK_RIG", key=key)
    cmds.parent(jointGrp, splineSpineIKRigGrp)
    cmds.parent(controlsGrp, splineSpineIKRigGrp)
    cmds.parent(ikHandle, splineSpineIKRigGrp)
    cmds.parent(duplicatedCurve, splineSpineIKRigGrp)

    ## Parent to base groups ##
    cmds.parent(splineSpineIKRigGrp, "RIG_GRP_ALL")

    # Clean-up: Delete tmp items
    cmds.delete(tmpJointNames)

    # Clean-up: lock and hide attributes
    #lockAttributes()

    # Ins and Outs
    ### Outs: Are like drivers, they control what happens to the inputs
    ### Ins: Are like the driven, they are being controlled by the outputs

    scale_in = splineSpineIKRigGrp
    addon_in = {
        "ikChain" : ikJoints,
        "fkChain" : fkJoints,
        "envChain" : envJoints,
        "switch" : switchControl,
        "ikCurve" : duplicatedCurve
    }

    pelvis_out = envJoints[0]
    spineTop_out = envJoints[-1]


    ### Add-ons ###
    # If an addon is added, determine which one and call the corresponding function
    scaleAxis = "Y"
    if addon == "SquashAndStretch":
        addon_SquashAndStretch(ikJoints, fkJoints, envJoints, switchControl, duplicatedCurve, scaleAxis, identifier)


    return scale_in, pelvis_out, spineTop_out, addon_in, key
