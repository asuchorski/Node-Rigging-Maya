//Maya ASCII 2022 scene
//Name: world.ma
//Last modified: Fri, Jun 21, 2024 03:50:30 PM
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
fileInfo "UUID" "3D60A1AC-4604-AA26-2266-7AB0FA20D7BE";
createNode transform -n "world";
	rename -uid "DFC2C803-4B88-942D-150F-40879258BDBF";
createNode nurbsCurve -n "nurbsCircleShape134334" -p "|world";
	rename -uid "74D23FA1-4F30-4025-2096-82B82A2C70FD";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8 9 10
		11
		3.9180581244561226 3.918058124456123 0
		3.392866161555456e-16 5.5409709377719381 0
		-3.9180581244561226 3.9180581244561221 0
		-5.5409709377719407 2.8724491187624153e-16 0
		-3.9180581244561226 -3.9180581244561226 0
		-5.5504284848016127e-16 -5.5409709377719416 0
		3.9180581244561226 -3.9180581244561221 0
		5.5409709377719407 -7.556202503899795e-16 0
		3.9180581244561226 3.918058124456123 0
		3.392866161555456e-16 5.5409709377719381 0
		-3.9180581244561226 3.9180581244561221 0
		;
createNode nurbsCurve -n "curveShape13" -p "|world";
	rename -uid "3401CD9C-4DD5-38DE-27B0-1383A95004C4";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		1 5 0 no 3
		6 0 1 2 3 4 5
		6
		0 5 0
		0 6 0
		-1 6 0
		0 7 0
		1 6 0
		0 6 0
		;
createNode nurbsCurve -n "curveShape2333" -p "|world";
	rename -uid "1D85DB28-487D-E57D-FFB4-2795306AD021";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		1 5 0 no 3
		6 0 1 2 3 4 5
		6
		5 0 0
		6 0 0
		6 1 0
		7 0 0
		6 -1 0
		6 0 0
		;
createNode nurbsCurve -n "curveShape33" -p "|world";
	rename -uid "2DCC9489-45FB-4A11-D08A-CE9321A78294";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		1 5 0 no 3
		6 0 1 2 3 4 5
		6
		6.1232339957367663e-16 -5 0
		7.3478807948841188e-16 -6 0
		1.0000000000000007 -6 0
		8.5725275940314722e-16 -7 0
		-0.99999999999999922 -6 0
		7.3478807948841188e-16 -6 0
		;
createNode nurbsCurve -n "curveShape4333" -p "|world";
	rename -uid "DF87FE47-4350-FD92-8C71-29914855FB67";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		1 5 0 no 3
		6 0 1 2 3 4 5
		6
		-5 -1.1102230246251565e-15 0
		-6 -1.3322676295501878e-15 0
		-6 -1.0000000000000013 0
		-7 -1.5543122344752192e-15 0
		-6 0.99999999999999867 0
		-6 -1.3322676295501878e-15 0
		;
createNode nurbsCurve -n "curveShape5333" -p "|world";
	rename -uid "F85858B5-4936-B7E4-99E2-8B8719A10FE5";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		1 5 0 no 3
		6 0 1 2 3 4 5
		6
		-3.5355339059327386 3.5355339059327369 0
		-4.2426406871192857 4.2426406871192839 0
		-4.9497474683058327 3.5355339059327364 0
		-4.9497474683058336 4.9497474683058318 0
		-3.5355339059327382 4.9497474683058318 0
		-4.2426406871192857 4.2426406871192839 0
		;
createNode nurbsCurve -n "curveShape63" -p "|world";
	rename -uid "3CD1B1C3-43A3-836A-BE44-1C93B2E39E1D";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		1 5 0 no 3
		6 0 1 2 3 4 5
		6
		3.5355339059327373 3.5355339059327386 0
		4.2426406871192848 4.2426406871192857 0
		3.5355339059327369 4.9497474683058336 0
		4.9497474683058318 4.9497474683058336 0
		4.9497474683058327 3.5355339059327378 0
		4.2426406871192848 4.2426406871192857 0
		;
createNode nurbsCurve -n "curveShape73333" -p "|world";
	rename -uid "423906C3-4DC9-68D9-24ED-6BAF4EAFE8AE";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		1 5 0 no 3
		6 0 1 2 3 4 5
		6
		-3.53553390593274 -3.5355339059327373 0
		-4.2426406871192883 -4.2426406871192848 0
		-3.5355339059327409 -4.9497474683058327 0
		-4.9497474683058362 -4.9497474683058318 0
		-4.9497474683058353 -3.5355339059327369 0
		-4.2426406871192883 -4.2426406871192848 0
		;
createNode nurbsCurve -n "curveShape833" -p "|world";
	rename -uid "67F22375-4EB8-2820-96B8-72AF3ECB655D";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		1 5 0 no 3
		6 0 1 2 3 4 5
		6
		3.5355339059327355 -3.5355339059327395 0
		4.242640687119283 -4.2426406871192874 0
		4.9497474683058309 -3.5355339059327404 0
		4.94974746830583 -4.9497474683058353 0
		3.5355339059327355 -4.9497474683058345 0
		4.242640687119283 -4.2426406871192874 0
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
// End of world.ma
