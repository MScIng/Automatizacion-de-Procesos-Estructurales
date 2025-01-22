import os
import sys
import comtypes.client

# True: Trabajará con el programa ETBAS que esté abierto
# False: Se abrirá el programa de manera Automaticade 
AttachToInstance = False

# True: para especificar manualmente la ruta a ETABS.exe
# False: se usará la última versión instalada de ETABS
SpecifyPath = True

# si el indicador anterior está en True, especifique la ruta a ETABS a continuación
ProgramPath = "C:\Program Files\Computers and Structures\ETABS 20\ETABS.exe"

# ruta completa del modelo 
# ajústelo a la ruta deseada de su modelo
APIPath = 'C:\CSi_ETABS_API_Example'
if not os.path.exists(APIPath):
    try:
        os.makedirs(APIPath)
    except OSError:
        pass
ModelPath = APIPath + os.sep + 'API_1-001.edb'

# crear objeto API helper
helper = comtypes.client.CreateObject('ETABSv1.Helper')
helper = helper.QueryInterface(comtypes.gen.ETABSv1.cHelper)

if AttachToInstance:
    try:
        # obtener el objeto ETABS activo
        myETABSObject = helper.GetObject("CSI.ETABS.API.ETABSObject") 
    except (OSError, comtypes.COMError):
        print("No running instance of the program found or failed to attach.")
        sys.exit(-1)
else:
    if SpecifyPath:
        try:
            # crear una instancia del objeto ETABS a partir de la ruta especificada
            myETABSObject = helper.CreateObject(ProgramPath)
        except (OSError, comtypes.COMError):
            print("Cannot start a new instance of the program from " + ProgramPath)
            sys.exit(-1)
    else:
        try: 
            # crear una instancia del objeto ETABS a partir del último ETABS instalado
            myETABSObject = helper.CreateObjectProgID("CSI.ETABS.API.ETABSObject") 
        except (OSError, comtypes.COMError):
            print("Cannot start a new instance of the program.")
            sys.exit(-1)

    # Comenzar la aplicacion de ETABS
    myETABSObject.ApplicationStart()

# Crear un objeto SapModel
SapModel = myETABSObject.SapModel

# Iniciar Modelo
SapModel.InitializeNewModel()

# Crear un modelo en blanco
ret = SapModel.File.NewBlank()

# Definir Propiedades del Material
MATERIAL_CONCRETE = 2
ret = SapModel.PropMaterial.SetMaterial('CONC', MATERIAL_CONCRETE)

# Asignar propiedades mecanicas isotropicas al material
ret = SapModel.PropMaterial.SetMPIsotropic('CONC', 3600, 0.2, 0.0000055)

# Definir las propiedades de Seccion a un Frame
ret = SapModel.PropFrame.SetRectangle('R1', 'CONC', 12, 12)

# Definir modificadores de propiedad a un Frame
ModValue = [1000, 0, 0, 1, 1, 1, 1, 1]
ret = SapModel.PropFrame.SetModifiers('R1', ModValue)

# Cambiar unidades a k-ft 
kip_ft_F = 4
ret = SapModel.SetPresentUnits(kip_ft_F)

# Crear un objeto Frame por Coordenadas
FrameName1 = ' '
FrameName2 = ' '
FrameName3 = ' '
[FrameName1, ret] = SapModel.FrameObj.AddByCoord(0, 0, 0, 0, 0, 10, FrameName1, 'R1', '1', 'Global')
[FrameName2, ret] = SapModel.FrameObj.AddByCoord(0, 0, 10, 8, 0, 16, FrameName2, 'R1', '2', 'Global')
[FrameName3, ret] = SapModel.FrameObj.AddByCoord(-4, 0, 10, 0, 0, 10, FrameName3, 'R1', '3', 'Global')

# Asignar resitricciones al punto de la Base
PointName1 = ' '
PointName2 = ' '
Restraint = [True, True, True, True, False, False]

[PointName1, PointName2, ret] = SapModel.FrameObj.GetPoints(FrameName1, PointName1, PointName2)
ret = SapModel.PointObj.SetRestraint(PointName1, Restraint)

# Asignar restricciones al punto superior
Restraint = [True, True, False, False, False, False]
[PointName1, PointName2, ret] = SapModel.FrameObj.GetPoints(FrameName2, PointName1, PointName2)
ret = SapModel.PointObj.SetRestraint(PointName2, Restraint)

# Refresar Vista
ret = SapModel.View.RefreshView(0, False)

# Asignar load patterns
LTYPE_OTHER = 8
ret = SapModel.LoadPatterns.Add('1', LTYPE_OTHER, 1, True)
ret = SapModel.LoadPatterns.Add('2', LTYPE_OTHER, 0, True)
ret = SapModel.LoadPatterns.Add('3', LTYPE_OTHER, 0, True)
ret = SapModel.LoadPatterns.Add('4', LTYPE_OTHER, 0, True)
ret = SapModel.LoadPatterns.Add('5', LTYPE_OTHER, 0, True)
ret = SapModel.LoadPatterns.Add('6', LTYPE_OTHER, 0, True)
ret = SapModel.LoadPatterns.Add('7', LTYPE_OTHER, 0, True)

# Asignar loading for load pattern 2
[PointName1, PointName2, ret] = SapModel.FrameObj.GetPoints(FrameName3, PointName1, PointName2)
PointLoadValue = [0,0,-10,0,0,0]
ret = SapModel.PointObj.SetLoadForce(PointName1, '2', PointLoadValue)
ret = SapModel.FrameObj.SetLoadDistributed(FrameName3, '2', 1, 10, 0, 1, 1.8, 1.8)

# Asignarloading for load pattern 3
[PointName1, PointName2, ret] = SapModel.FrameObj.GetPoints(FrameName3, PointName1, PointName2)
PointLoadValue = [0,0,-17.2,0,-54.4,0]
ret = SapModel.PointObj.SetLoadForce(PointName2, '3', PointLoadValue)

# Asignar loading for load pattern 4
ret = SapModel.FrameObj.SetLoadDistributed(FrameName2, '4', 1, 11, 0, 1, 2, 2)

# Asignar loading for load pattern 5
ret = SapModel.FrameObj.SetLoadDistributed(FrameName1, '5', 1, 2, 0, 1, 2, 2, 'Local')
ret = SapModel.FrameObj.SetLoadDistributed(FrameName2, '5', 1, 2, 0, 1, -2, -2, 'Local')

# Asignar loading for load pattern 6
ret = SapModel.FrameObj.SetLoadDistributed(FrameName1, '6', 1, 2, 0, 1, 0.9984, 0.3744, 'Local')
ret = SapModel.FrameObj.SetLoadDistributed(FrameName2, '6', 1, 2, 0, 1, -0.3744, 0, 'Local')

# Asignar loading for load pattern 7
ret = SapModel.FrameObj.SetLoadPoint(FrameName2, '7', 1, 2, 0.5, -15, 'Local')

# Cambiar unidades de Trabajo k-in units
kip_in_F = 3
ret = SapModel.SetPresentUnits(kip_in_F)

# Guardar modelo en una ubicacion dada
ret = SapModel.File.Save(ModelPath)

# Correr Modelo (Esto creará un Modelo de Analisis)
ret = SapModel.Analyze.RunAnalysis()

# Inicializar los resultados
ProgramResult = [0,0,0,0,0,0,0]
[PointName1, PointName2, ret] = SapModel.FrameObj.GetPoints(FrameName2, PointName1, PointName2)

# get results for load cases 1 through 7
for i in range(0,7):
      NumberResults = 0
      Obj = []
      Elm = []
      ACase = []
      StepType = []
      StepNum = []
      U1 = []
      U2 = []
      U3 = []
      R1 = []
      R2 = []
      R3 = []
      ObjectElm = 0
      ret = SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
      ret = SapModel.Results.Setup.SetCaseSelectedForOutput(str(i + 1))
      if i <= 3:
          [NumberResults, Obj, Elm, ACase, StepType, StepNum, U1, U2, U3, R1, R2, R3, ret] = SapModel.Results.JointDispl(PointName2, ObjectElm, NumberResults, Obj, Elm, ACase, StepType, StepNum, U1, U2, U3, R1, R2, R3)
          ProgramResult[i] = U3[0]
      else:
          [NumberResults, Obj, Elm, ACase, StepType, StepNum, U1, U2, U3, R1, R2, R3, ret] = SapModel.Results.JointDispl(PointName1, ObjectElm, NumberResults, Obj, Elm, ACase, StepType, StepNum, U1, U2, U3, R1, R2, R3)
          ProgramResult[i] = U1[0]

# Cerrar ETABS
ret = myETABSObject.ApplicationExit(False)
SapModel = None
myETABSObject = None

# fill independent results
IndResult = [0,0,0,0,0,0,0]
IndResult[0] = -0.02639
IndResult[1] = 0.06296
IndResult[2] = 0.06296
IndResult[3] = -0.2963
IndResult[4] = 0.3125
IndResult[5] = 0.11556
IndResult[6] = 0.00651

# fill percent difference
PercentDiff = [0,0,0,0,0,0,0]
for i in range(0,7):
      PercentDiff[i] = (ProgramResult[i] / IndResult[i]) - 1

# display results
for i in range(0,7):
      print()
      print(ProgramResult[i])
      print(IndResult[i])
      print(PercentDiff[i])
