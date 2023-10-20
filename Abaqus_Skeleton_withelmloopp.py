"""
Adapted by Collette Gillaspie (2021)
You may need to adjust the spacing of this script (Edit --> Blank Operations) to run in Abaqus.
"""
from abaqus import *
from abaqusConstants import *
import __main__
import section
import odbSection
import regionToolset
import displayGroupMdbToolset as dgm
import part
import material
import assembly
import step
import interaction
import load
import mesh
import job
import sketch
import visualization
import xyPlot
import connectorBehavior
import displayGroupOdbToolset as dgo
from math import atan, sin, cos, tan
from Post_P_Script import getResults

# Write data file column headings
DataFile = open('PostData.txt','w')
DataFile.write('seedSize tipDisp \n')
DataFile.close()
session.journalOptions.setValues(replayGeometry=COORDINATE, recoverGeometry=COORDINATE)

# Start Loop
elemType = [CPE3,CPE6,CPE4,CPE4I,CPE8,CPE8R]
seedSize = [0.25,0.125,0.10,0.20,0.75]
for element in elemType:
	for sizes in seedSize:

		Mdb() 

		# Sketch Geometry and Create Parts
		print 'Sketching/Creating Part'
		
		s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=20.0)
		g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
		s.setPrimaryObject(option=STANDALONE)
		s.rectangle(point1=(0.0, 0.0), point2=(12.0, 0.5))
		p = mdb.models['Model-1'].Part(name='beam', dimensionality=TWO_D_PLANAR, 
			type=DEFORMABLE_BODY)
		p = mdb.models['Model-1'].parts['beam']
		p.BaseShell(sketch=s)
		s.unsetPrimaryObject()
		del mdb.models['Model-1'].sketches['__profile__']

		# Define Face Partitions
		print 'Partitioning Part'

		p = mdb.models['Model-1'].parts['beam']
		p.DatumPlaneByPrincipalPlane(principalPlane=YZPLANE, offset=4.0)
		p.DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=0.25)
		p = mdb.models['Model-1'].parts['beam']
		d1 = p.datums
		p.PartitionFaceByDatumPlane(datumPlane=d1[2], faces=p.faces)
		p = mdb.models['Model-1'].parts['beam']
		d2 = p.datums
		p.PartitionFaceByDatumPlane(datumPlane=d2[3], faces=p.faces)	

		# Create Material
		print 'Creating Materials'
			
		mdb.models['Model-1'].Material(name='aluminum')
		mdb.models['Model-1'].materials['aluminum'].Elastic(table=((10000000.0, 0.3), 
		))
		
		# Create Section
		print 'Creating Sections'
		
		mdb.models['Model-1'].HomogeneousSolidSection(name='BeamSection', 
			material='aluminum', thickness=2.0)

		# Assign Section
		print 'Assigning Sections'
		
		p = mdb.models['Model-1'].parts['beam']
		region = p.Set(faces=p.faces, name='Set-1')
		p = mdb.models['Model-1'].parts['beam']
		p.SectionAssignment(region=region, sectionName='BeamSection', offset=0.0, 
			offsetType=MIDDLE_SURFACE, offsetField='', 
			thicknessAssignment=FROM_SECTION)

		# Assemble Parts
		print 'Placing Parts in Space'
		# Create Instances here
		a = mdb.models['Model-1'].rootAssembly
		a.DatumCsysByDefault(CARTESIAN)
		p = mdb.models['Model-1'].parts['beam']
		a.Instance(name='beam-1', part=p, dependent=ON)

		# Define Steps
		print 'Defining Steps'

		mdb.models['Model-1'].StaticStep(name='Step-1', previous='Initial')

		# Create Loads
		print 'Defining Loads'
		
		a = mdb.models['Model-1'].rootAssembly
		s1 = a.instances['beam-1'].edges
		side1Edges1 = s1.findAt(((1.0, 0.5, 0.0), ), ((6.0, 0.5, 0.0), ))
		region = a.Surface(side1Edges=side1Edges1, name='Surf-1')
		mdb.models['Model-1'].Pressure(name='pressure', createStepName='Step-1', 
			region=region, distributionType=UNIFORM, field='', magnitude=10.0, 
			amplitude=UNSET)

			
		# Define BCs
		print 'Defining BCs'

		a = mdb.models['Model-1'].rootAssembly
		e1 = a.instances['beam-1'].edges
		edges1 = e1.findAt(((0.0, 0.0625, 0.0), ), ((0.0, 0.3125, 0.0), ))
		region = a.Set(edges=edges1, name='Set-1')
		mdb.models['Model-1'].EncastreBC(name='fixedend', createStepName='Step-1', 
			region=region, localCsys=None)
		
		# Define Sets
		print 'Defining Sets'
		# Note: Create "TIPNODE" here
		# Create the set from the Assembly module (not Part)

		a = mdb.models['Model-1'].rootAssembly
		v1 = a.instances['beam-1'].vertices
		verts1 = v1.findAt(((12.0, 0.25, 0.0), ))
		a.Set(vertices=verts1, name='TIPNODE')	

		# Mesh Parts
		print 'Meshing Part'

		p = mdb.models['Model-1'].parts['beam']
		p.seedPart(size=sizes, deviationFactor=0.1, minSizeFactor=0.1)
		f = p.faces
		pickedRegions = f.findAt(((9.333333, 0.166667, 0.0), ), ((2.666667, 0.166667, 
			0.0), ), ((1.333333, 0.333333, 0.0), ), ((6.666667, 0.333333, 0.0), ))
		p.setMeshControls(regions=pickedRegions, elemShape=QUAD, technique=STRUCTURED)
		p = mdb.models['Model-1'].parts['beam']
		p.generateMesh()
		elemType1 = mesh.ElemType(elemCode=element, elemLibrary=STANDARD)
		p = mdb.models['Model-1'].parts['beam']
		f = p.faces
		faces = f.findAt(((9.333333, 0.166667, 0.0), ), ((2.666667, 0.166667, 0.0), ), 
			((1.333333, 0.333333, 0.0), ), ((6.666667, 0.333333, 0.0), ))
		pickedRegions =(faces, )
		p.setElementType(regions=pickedRegions, elemTypes=(elemType1, ))
		

		# Create Optimization Task (604 ONLY)
		print 'Creating Optimization Task'

		# Create Design Responses (604 ONLY)
		print 'Creating Design Responses'

		# Create Objective Function (604 ONLY)
		print 'Creating Objective Function'

		# Create Optimization Constraints (604 ONLY)
		print 'Creating Optimization Constraints'

		# Create Geometric Restrictions With No Frozen Elements (604 ONLY)
		print 'Creating Geometric Restrictions'

		##############################################
		### Creation/Execution of the Optimization ###
		##############################################
		# 604 Students: Please note the commented changes you will make to this script for Homework 4, Problem 4
		
		print 'Creating/Running Optimization'
		ModelName='Model-1'
		# 604 ONLY Change for Optimization:
		#ModelName='Opt-Process-1'

		mdb.Job(name=ModelName, model=ModelName, description='', type=ANALYSIS, 
			atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
			memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
			explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
			modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
			scratch='', multiprocessingMode=DEFAULT, numCpus=1, numGPUs=0)
		job=mdb.jobs[ModelName]
		# 604 ONLY Change for Optimization:
		#mdb.OptimizationProcess(name=ModelName, model='Model-1', task='Task-1', 
		#	 description='', prototypeJob='Opt-Process-1-Job', maxDesignCycle=15, 
		#	 odbMergeFrequency=2, dataSaveFrequency=OPT_DATASAVE_SPECIFY_CYCLE)
		#mdb.optimizationProcesses['Opt-Process-1'].Job(name='Opt-Process-1-Job', 
		#	 model='Model-1', atTime=None, waitMinutes=0, waitHours=0, queue=None, 
		#	 memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
		#	 multiprocessingMode=DEFAULT, numCpus=4, numDomains=4, numGPUs=0)
		#job=mdb.optimizationProcesses[ModelName]

		# Delete lock file, if it exists
		if os.access('%s.lck'%ModelName,os.F_OK):
			os.remove('%s.lck'%ModelName)
			
		# Run job, then process results.
		job.submit()
		job.waitForCompletion()
		print 'Completed job'

		# 604 ONLY Change for Optimization (note that you will need to adjust optResultLocation):
		#a = mdb.models['Model-1'].rootAssembly
		#mdb.CombineOptResults(
			#optResultLocation='C:\\Users\\NETID\\Documents\\Opt-Process-1', 
			#includeResultsFrom=INITIAL, optIter=INITIAL_AND_LAST, models=ALL, steps=(
			#'Step-1', ), analysisFieldVariables=('S', 'U'))
		#ModelName='Opt-Process-1\TOSCA_POST\Opt-Process-1-Job_post'
		
		# Uncomment to retrieve the mass of your model where ModelName is a string.
		#prop = mdb.models[ModelName].rootAssembly.getMassProperties()
		#mass = prop['mass']
		
		tipDisp = getResults(ModelName)
		DataFile = open('PostData.txt','a')
		DataFile.write('%10f %10f\n' % (sizes,tipDisp))
		DataFile.close()
	print 'getting the bag'
print 'Bag secured.'