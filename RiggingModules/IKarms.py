import maya.cmds as cmds  # type: ignore
from addon_SquashAndStretch import addon_SquashAndStretch
from functionality import importer, templateImporter, createOffsetGrp, matchTransform, createGroup, createJoints, constraintJointChains, createFKControls, setupIKFKSwitch, setupIKFKVisibility, lockAttributes
from storeObjectsInJSON import loadGeneratedObjects, cleanSpecificList, addObjectToList

generatedObjects = loadGeneratedObjects()  # Load existing data from JSON file at the start

def template(identifier = "NULL"):
    key = "TBIKTEMP_" + identifier
    cleanSpecificList(key)
    templateImporter("Scenes\\Templates\\twoBoneIK.ma", key)

# Creates a two bone IK setup
def twoBoneIK(twistJoints = 0, addon = "NULL", identifier = "NULL"):
    cmds.select(clear=True)

    # Define the key that will be used in every object created by the code to identifiy it
    key = "TBIK_" + identifier
    tempKey = "TBIKTEMP_" + identifier

    locators = ["shoulder_LOC_" + tempKey, "elbow_LOC_" + tempKey, "wrist_LOC_" + tempKey, "poleVec_LOC_" + tempKey]
    ikJointNames = ["shoulder_IK_" + key + "_JNT", "elbow_IK_" + key + "_JNT", "wrist_IK_" + key + "_JNT"]
    fkJointNames = ["shoulder_FK_" + key + "_JNT", "elbow_FK_" + key + "_JNT", "wrist_FK_" + key + "_JNT"]
    envJointNames = ["shoulder_ENV_" + key + "_JNT", "elbow_ENV_" + key + "_JNT", "wrist_ENV_" + key + "_JNT"]

    ikJoints = []
    fkJoints = []
    envJoints = []
    locatorPositions = {}
    

    cleanSpecificList(key)  # Clean any existing objects in the 'twoBoneIK' list

    ikArmsCurve = "ArmIK_Curve_" + tempKey

    # IK Joints
    jointsIK = createJoints(jointNames=ikJointNames, joints=ikJoints, locators=locators, locatorPositions=locatorPositions, key=key)[0]
    # FK Joints
    createJoints(jointNames=fkJointNames, joints=fkJoints, locators=locators, locatorPositions=locatorPositions, key=key)
    # ENV Joints
    envJoitns = createJoints(jointNames=envJointNames, joints=envJoints, locators=locators, locatorPositions=locatorPositions, key=key)[0]

    # Create point and orientconstraints between ik, fk and env joints
    constraintJointChains(rootJntOne=ikJoints[0], rootJntTwo=envJoints[0], key=key)
    constraintJointChains(rootJntOne=fkJoints[0], rootJntTwo=envJoints[0], key=key)

    # Function to create fk controls and position them
    fkControls,fkControlOffsetGrps = createFKControls(control="Scenes\\circle.ma", fkChain=fkJoints, key=key, rotOffset=[0,90,0])

    switchControl = importer(item="Scenes\\arrow.ma", name="Arm_Settings_" + key, key=key, scale = [0.25, 0.25, 0.25], lineWidth=2.0, colour=6)
    setupIKFKSwitch(envChain=envJoints, fkChain=fkJoints, ikChain=ikJoints, switchCtrl=switchControl, key=key )
    switchOffsetGrp = createOffsetGrp(item=switchControl, key=key)
    matchTransform(source=switchOffsetGrp, target=locators[1], transOffset=[0,4,0], rotOffset=[90,0,90])

    # Create IK arm control and move it into place
    armControl = importer(item="Scenes\\cube.ma", name="Arm_CTRL_" + key , key=key, colour=17)
    wristPos = locatorPositions.get("wrist_LOC_" + tempKey)
    cmds.xform(armControl, worldSpace=True, translation=wristPos)
    cmds.makeIdentity(armControl, apply=True, translate=True, rotate=True, scale=True, normal=False)
    armControlOffsetGrp = createOffsetGrp(armControl, key)

    # Create IK solver
    ikHandle = cmds.ikHandle(name="ArmIKHandle_" + key, startJoint=ikJoints[0], endEffector=ikJoints[-1], solver="ikRPsolver")[0]
    cmds.parent(ikHandle, armControl)
    addObjectToList(key, ikHandle)

    # Create pole vector
    poleVectorControl = importer(item="Scenes\\circlePinched.ma", name="PoleVec_CTRL_" + key, key=key, colour=13)
    matchTransform(poleVectorControl, locators[3])
    poleVectorOffsetGrp = createOffsetGrp(poleVectorControl, key)
    poleVector = cmds.poleVectorConstraint(poleVectorControl, ikHandle)[0]
    addObjectToList(key, poleVector)

    # Create curve and the clusters for each cv parenting the last cv to arm control so the curve stretches but doesnt compress
    duplicatedCurve = cmds.duplicate(ikArmsCurve, name=ikArmsCurve + "_IK_" + key)[0]
    cmds.parent(duplicatedCurve, world=True)
    cmds.setAttr(duplicatedCurve + ".template", 0)
    addObjectToList(key, duplicatedCurve)

    duplicatedCurveShape = cmds.listRelatives(duplicatedCurve, shapes=True)[0]

    curveClusters = []

    # Cluster 1: CVs 0 and 1
    cluster1 = cmds.cluster(f"{duplicatedCurveShape}.cv[0]", f"{duplicatedCurveShape}.cv[1]",
                            name=f"{duplicatedCurve}_cluster1")[1]
    cmds.parentConstraint(poleVectorControl, cluster1, maintainOffset=True)
    cmds.setAttr(f"{cluster1}.visibility", 0)
    curveClusters.append(cluster1)

    # Cluster 2: CV 2
    cluster2 = cmds.cluster(f"{duplicatedCurveShape}.cv[2]",
                            name=f"{duplicatedCurve}_cluster2")[1]
    cmds.parentConstraint(poleVectorControl, cluster2, maintainOffset=True)
    cmds.setAttr(f"{cluster2}.visibility", 0)
    curveClusters.append(cluster2)

    # Cluster 3: CVs 3 and 4
    cluster3 = cmds.cluster(f"{duplicatedCurveShape}.cv[3]", f"{duplicatedCurveShape}.cv[4]",
                            name=f"{duplicatedCurve}_cluster3")[1]
    cmds.parentConstraint(armControl, cluster3, maintainOffset=True)
    cmds.setAttr(f"{cluster3}.visibility", 0)
    curveClusters.append(cluster3)

            


    # IK-FK switching visibility
    setupIKFKVisibility(fkControls=fkControls, ikControls=[armControl, poleVectorControl], switchCtrl=switchControl, key=key)

    # Final Clean-Ups: Group remaining items
    jointsGroup = createGroup("joints", key)
    cmds.parent(ikJoints[0], jointsGroup)
    cmds.parent(fkJoints[0], jointsGroup)
    cmds.parent(envJoints[0], jointsGroup)
    
    controlGroup = createGroup("controls", key)
    
    twoBoneIKGrp = createGroup("armIK_RIG", key)
    cmds.parent(controlGroup, twoBoneIKGrp)
    cmds.parent(jointsGroup, twoBoneIKGrp)

    ikControlGroup = createGroup(name="IK_CTRL_GRP", key=key)
    fkControlGroup = createGroup(name="FK_CTRL_GRP", key=key)

    cmds.parent(fkControlOffsetGrps[0], fkControlGroup)
    cmds.parent(poleVectorOffsetGrp, ikControlGroup)
    cmds.parent(armControlOffsetGrp, ikControlGroup)

    cmds.parent(ikControlGroup, controlGroup)
    cmds.parent(fkControlGroup, controlGroup)
    cmds.parent(switchOffsetGrp, controlGroup)

    curveGroup = createGroup("curve", key)
    cmds.parent(curveClusters, curveGroup)
    cmds.parent(duplicatedCurve, curveGroup)
    cmds.parent(curveGroup, twoBoneIKGrp)

    ## Parent to base groups ##

    cmds.parent(twoBoneIKGrp, "RIG_GRP_ALL")

    # Final Clean-Ups: Lock and hide attributes
    lockAttributes(item=switchControl, vis= 1, trans = 1, rot = 1, scale = 1, hidden = 1)
    lockAttributes(item=armControl, scale = 1, hidden = 1)
    lockAttributes(item=poleVectorControl, scale = 1, hidden = 1)

    # Ins and Outs
    ### Outs: Are like drivers, they control what happens to the inputs
    ### Ins: Are like the driven, they are being controlled by the outputs

    shoulderIK_in = jointsIK[0]
    poleVectorIK_in = poleVectorOffsetGrp
    shoulderFK_in = fkControlOffsetGrps[0]
    scale_in = twoBoneIKGrp

    wrist_out = envJoitns[-1]

    ### Add-ons ###
    # If an addon is added, determine which one and call the corresponding function
    scaleAxis = "X"
    if addon == "SquashAndStretch":
        addon_SquashAndStretch(jointsIK, fkJoints, envJoitns, switchControl, duplicatedCurve, scaleAxis, identifier)

    return scale_in, shoulderIK_in, poleVectorIK_in, shoulderFK_in, wrist_out, key