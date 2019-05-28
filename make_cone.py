import bpy

datadir = '/home/pdmurray/Desktop/Workspace/simtoblender/sp4.out/'
nframes = 100
scaling = 1e7
step = 13
radius = .03
length = .03
vertices = 32
time_dilation_factor = 1 # Must be int



# Read the location of the magnetization vectors from centerlocs.csv
with open(datadir + 'centerlocs.csv', 'r') as f:
    lines = f.readlines()

# Ignore comment lines at the top of the file
i_start = 0
while lines[i_start][0] == '#':
    i_start += 1
    
# Extract the location of each cell
x, y, z = [], [], []
for line in lines[i_start::step]:
    s = line.split(',')
    x.append(float(s[0])*scaling)
    y.append(float(s[1])*scaling)
    z.append(float(s[2])*scaling)

# Generate a new cone mesh for each location. The name of the cones should be the Cone.###, where the number is the order in which it was added.
for _x, _y, _z in zip(x, y, z):
    bpy.ops.mesh.primitive_cone_add(vertices=vertices,radius1=radius,radius2=0.0,depth=length,location=(_x, _y, _z))
bpy.data.meshes['Cone'].name = 'Cone.000'


# Rotate and keyframe for each Rodrigues file
for i in range(nframes):
    with open(datadir + f'rodrigues{i:06d}.csv', 'r') as f:
        lines = f.readlines()
        
    i_start = 0
    while lines[i_start][0] == '#':
        i_start += 1
        
    axes = []
    angles = []
    for line in lines[i_start::step]:
        s = line.split(',')
        axes.append([float(s[3]), float(s[4]), float(s[5])])
        angles.append(float(s[6]))
        
    for object, axis, angle in zip(bpy.data.objects, axes, angles):
        object.rotation_mode = 'AXIS_ANGLE'
        object.rotation_axis_angle = [angle, axis[0], axis[1], axis[2]]
        object.keyframe_insert(data_path='rotation_axis_angle', frame=i*time_dilation_factor)
        object.rotation_axis_angle = [-angle, axis[0], axis[1], axis[2]]
