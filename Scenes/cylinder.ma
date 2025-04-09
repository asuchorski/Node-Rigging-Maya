//Maya ASCII 2022 scene
//Name: cylinder.ma
//Last modified: Fri, Jun 21, 2024 03:50:45 PM
//Codeset: 1252
requires maya "2022";
requires "stereoCamera" "10.0";
requires "mtoa" "5.0.0.4";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2022";
fileInfo "version" "2022";
fileInfo "cutIdentifier" "202405021833-753375ecb3";
fileInfo "osv" "Windows 10 Pro v2009 (Build: 22631)";
fileInfo "UUID" "9E19B4F6-4CB5-F30D-320C-BEAC1FB68706";
createNode transform -n "cylinder";
	rename -uid "38191A61-48C7-82EB-7981-4F915DB6C431";
	setAttr ".rp" -type "double3" 0 -3.3306690738754696e-16 1.5 ;
	setAttr ".sp" -type "double3" 0 -3.3306690738754696e-16 1.5 ;
createNode nurbsCurve -n "nurbsCircleShape134335" -p "cylinder";
	rename -uid "FD5A1EFF-465F-58D2-B03A-4AA24504329E";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8 9 10
		11
		0.78361162489122449 0.7836116248912246 0
		6.7857323231109122e-17 1.1081941875543877 0
		-0.78361162489122449 0.78361162489122438 0
		-1.1081941875543881 5.7448982375248304e-17 0
		-0.78361162489122449 -0.78361162489122449 0
		-1.1100856969603225e-16 -1.1081941875543884 0
		0.78361162489122449 -0.78361162489122438 0
		1.1081941875543881 -1.511240500779959e-16 0
		0.78361162489122449 0.7836116248912246 0
		6.7857323231109122e-17 1.1081941875543877 0
		-0.78361162489122449 0.78361162489122438 0
		;
createNode nurbsCurve -n "nurbsCircleShape134336" -p "cylinder";
	rename -uid "00023D3B-4962-2C0B-4F8F-71A1DEE818EF";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8 9 10
		11
		0.78361162489122449 0.7836116248912246 3
		6.7857323231109122e-17 1.1081941875543877 3
		-0.78361162489122449 0.78361162489122438 3
		-1.1081941875543881 5.7448982375248304e-17 3
		-0.78361162489122449 -0.78361162489122449 3
		-1.1100856969603225e-16 -1.1081941875543884 3
		0.78361162489122449 -0.78361162489122438 3
		1.1081941875543881 -1.511240500779959e-16 3
		0.78361162489122449 0.7836116248912246 3
		6.7857323231109122e-17 1.1081941875543877 3
		-0.78361162489122449 0.78361162489122438 3
		;
createNode nurbsCurve -n "curve3rfdfShape" -p "cylinder";
	rename -uid "550E7767-406B-A23C-266B-5095FE5C0F8E";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 -1 0
		0 -1 3
		;
createNode nurbsCurve -n "curve4ffffShape" -p "cylinder";
	rename -uid "6B83568B-4C04-17CE-9588-82A8672FEF40";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0 1 0
		0 1 3
		;
createNode nurbsCurve -n "curveShape543434" -p "cylinder";
	rename -uid "BBC62480-4D07-A34A-2BEA-73A36D76907B";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		1 0 0
		1 0 3
		;
createNode nurbsCurve -n "rrrrShape" -p "cylinder";
	rename -uid "09CFC551-4318-1674-22FC-FB815E716DDA";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		-1 0 0
		-1 0 3
		;
createNode nurbsCurve -n "curveShape73434" -p "cylinder";
	rename -uid "F00926E4-4DB0-8B02-7743-30A10B4194F6";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		-0.66767459425863285 -0.74420463294030625 0
		-0.66767459425863285 -0.74420463294030625 3
		;
createNode nurbsCurve -n "curveShape83434" -p "cylinder";
	rename -uid "170A3495-4795-FC85-EDC8-9BA5125DF75F";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		-0.68745351074640992 0.73663749698886782 0
		-0.68745351074640992 0.73663749698886782 3
		;
createNode nurbsCurve -n "curveShape93434" -p "cylinder";
	rename -uid "37CD653B-4A9D-6B72-071E-54AAF59DA261";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0.7638250304532459 0.63938973871667915 0
		0.7638250304532459 0.63938973871667915 3
		;
createNode nurbsCurve -n "curveShape103234" -p "cylinder";
	rename -uid "54D8ECEB-4FDE-1785-16A9-14896B01DBC5";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		1 1 0 no 3
		2 0 1
		2
		0.65339206396760208 -0.75593820063162553 0
		0.65339206396760208 -0.75593820063162553 3
		;
select -ne :time1;
	setAttr ".o" 1;
	setAttr ".unw" 1;
select -ne :hardwareRenderingGlobals;
	setAttr ".otfna" -type "stringArray" 22 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surface" "Particles" "Particle Instance" "Fluids" "Strokes" "Image Planes" "UI" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Hair Systems" "Follicles" "Misc. UI" "Ornaments"  ;
	setAttr ".otfva" -type "Int32Array" 22 0 1 1 1 1 1
		 1 1 1 0 0 0 0 0 0 0 0 0
		 0 0 0 0 ;
	setAttr ".fprt" yes;
select -ne :renderPartition;
	setAttr -s 2 ".st";
select -ne :renderGlobalsList1;
select -ne :defaultShaderList1;
	setAttr -s 5 ".s";
select -ne :postProcessList1;
	setAttr -s 2 ".p";
select -ne :defaultRenderingList1;
select -ne :initialShadingGroup;
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr ".ro" yes;
select -ne :defaultRenderGlobals;
	addAttr -ci true -h true -sn "dss" -ln "defaultSurfaceShader" -dt "string";
	setAttr ".ren" -type "string" "arnold";
	setAttr ".dss" -type "string" "lambert1";
select -ne :defaultResolution;
	setAttr ".pa" 1;
select -ne :defaultColorMgtGlobals;
	setAttr ".cfe" yes;
	setAttr ".cfp" -type "string" "<MAYA_RESOURCES>/OCIO-configs/Maya2022-default/config.ocio";
	setAttr ".vtn" -type "string" "ACES 1.0 SDR-video (sRGB)";
	setAttr ".vn" -type "string" "ACES 1.0 SDR-video";
	setAttr ".dn" -type "string" "sRGB";
	setAttr ".wsn" -type "string" "ACEScg";
	setAttr ".otn" -type "string" "ACES 1.0 SDR-video (sRGB)";
	setAttr ".potn" -type "string" "ACES 1.0 SDR-video (sRGB)";
select -ne :hardwareRenderGlobals;
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
// End of cylinder.ma
