//Maya ASCII 2022 scene
//Name: square.ma
//Last modified: Fri, Jun 21, 2024 03:51:03 PM
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
fileInfo "UUID" "88C91829-491E-9A8C-07CE-1EB2D22CC46D";
createNode transform -n "square";
	rename -uid "DCD23AC5-4C51-97B3-F820-D68DA8C5B3E8";
	setAttr ".rp" -type "double3" 0 1.1102230246251565e-16 0 ;
	setAttr ".sp" -type "double3" 0 1.1102230246251565e-16 0 ;
createNode nurbsCurve -n "topnurbsSquareShape1" -p "square";
	rename -uid "FF8D1591-4156-ACBD-3B91-2A8D0FC6F0A1";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		3 1 0 no 3
		6 0 0 0 1 1 1
		4
		0.5 0.50000000000000011 0
		0.5 0.1666666666666668 0
		0.5 -0.16666666666666652 0
		0.5 -0.49999999999999983 0
		;
createNode nurbsCurve -n "leftnurbsSquareShape1" -p "square";
	rename -uid "DE80B733-4F95-D040-EDD2-70B792CCB5F9";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		3 1 0 no 3
		6 0 0 0 1 1 1
		4
		0.5 -0.49999999999999989 0
		0.16666666666666669 -0.49999999999999989 0
		-0.16666666666666663 -0.49999999999999989 0
		-0.49999999999999994 -0.49999999999999989 0
		;
createNode nurbsCurve -n "bottomnurbsSquareShape1" -p "square";
	rename -uid "1E26546C-4CCD-50B4-B2E6-41A91F9B3EFF";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		3 1 0 no 3
		6 0 0 0 1 1 1
		4
		-0.5 -0.49999999999999989 0
		-0.5 -0.16666666666666657 0
		-0.5 0.16666666666666674 0
		-0.5 0.5 0
		;
createNode nurbsCurve -n "rightnurbsSquareShape1" -p "square";
	rename -uid "32459833-4FEC-B378-0E8D-13BE9794F1E2";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		3 1 0 no 3
		6 0 0 0 1 1 1
		4
		-0.5 0.50000000000000011 0
		-0.16666666666666669 0.50000000000000011 0
		0.16666666666666663 0.50000000000000011 0
		0.49999999999999994 0.50000000000000011 0
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
// End of square.ma
