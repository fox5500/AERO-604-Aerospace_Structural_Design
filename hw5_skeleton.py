# Ethan Fox Aerospace Structural Design HW5

# Define Vars
h0 = .5
hL = [figure out how to loop and replace values] #doe to detemerine best number using paerto front then loop through and replace with genetic alg
L = 1
F = 5*10^6
t = 10*h0
tau = F/[t*hL]



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





		