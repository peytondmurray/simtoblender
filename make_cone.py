import bpy
import numpy as np

root = '/home/pdmurray/Desktop/Workspace/simtoblender/'
datadir = 'bloch_nucleation_mx.out/'
nframes = 100
scaling = 5e7
step = 39
radius = .15
length = .3
vertices = 32
time_dilation_factor = 1 # Must be int



div_m = []
for i in range(nframes):
    with open(root + datadir + f'rodrigues{i:06d}.csv', 'r') as f:
        lines = f.readlines()
        
    i_start = 0
    while lines[i_start][0] == '#':
        i_start += 1
    
    for line in lines[i_start:]:
        s = line.split(',')
        div_m.append(float(s[-1]))
        
min_div_m = np.min(div_m)
max_div_m = np.max(div_m)

# Generate new colors/materials which span the color space
with open(root + 'colors.csv', 'r') as f:
    lines = f.readlines()
colors = np.array([list(map(float, line.split())) for line in lines])
divergences = np.linspace(min_div_m, max_div_m, len(colors))        

# Read the location of the magnetization vectors from centerlocs.csv
with open(root + datadir + 'centerlocs.csv', 'r') as f:
    lines = f.readlines()

# Ignore comment lines at the top of the file
i_start = 0
while lines[i_start][0] == '#':
    i_start += 1
    
# Extract the location of each cell
x, y, z = [], [], []
ix, iy, iz = [], [], []
for line in lines[i_start::step]:
    s = line.split(',')
    ix.append(int(s[0]))
    iy.append(int(s[1]))
    iz.append(int(s[2]))
    x.append(float(s[3])*scaling)
    y.append(float(s[4])*scaling)
    z.append(float(s[5])*scaling)
    
# Generate a new cone mesh for each location. The name of the cones should be the Cone.###, where the number is the order in which it was added.
bpy.ops.mesh.primitive_cone_add(vertices=vertices,radius1=radius,radius2=0.0,depth=length,location=(0, 0, 0))
base_cone = bpy.context.active_object
base_cone.name = f'base_cone'
base_cone.rotation_mode = 'AXIS_ANGLE'

for i, (_ix, _iy, _iz, _x, _y, _z) in enumerate(zip(ix, iy, iz, x, y, z)):
    #bpy.ops.mesh.primitive_cone_add(vertices=vertices,radius1=radius,radius2=0.0,depth=length,location=(_x, _y, _z))
    #bpy.context.active_object.name = f'Cone({_ix},{_iy},{_iz})'
    #bpy.context.active_object.rotation_mode = 'AXIS_ANGLE'
    m = base_cone.copy()
    bpy.context.scene.collection.objects.link(m)
    m.location = (_x, _y, _z)
    new_mat = bpy.data.materials.new(name=f'Cone({_ix},{_iy},{_iz})')
    new_mat.use_nodes = True
    bpy.context.active_object.data.materials.append(new_mat)

bpy.data.objects.remove(base_cone)

# Rotate and keyframe for each Rodrigues file
for i in range(nframes):
    with open(root + datadir + f'rodrigues{i:06d}.csv', 'r') as f:
        lines = f.readlines()
        
    i_start = 0
    while lines[i_start][0] == '#':
        i_start += 1
        
    axes = []
    angles = []
    div = []
    ix, iy, iz = [], [], []
    for line in lines[i_start::step]:
        s = line.split(',')
        ix.append(int(s[0]))
        iy.append(int(s[1]))
        iz.append(int(s[2]))
        axes.append([float(s[3]), float(s[4]), float(s[5])])
        angles.append(float(s[6]))
        div.append(float(s[7]))
        
#    for object, axis, angle in zip(bpy.data.objects, axes, angles):
    for _ix, _iy, _iz, axis, angle, _div in list(zip(ix, iy, iz, axes, angles, div)):#[::step]:
        color = colors[np.argmin(np.abs(divergences - _div))]
#        color = colors[(len(colors)-1)*int((np.max(div) - _div)/(np.max(div) - np.min(div)))]
        object = bpy.data.objects[f'Cone({_ix},{_iy},{_iz})']
        object.rotation_axis_angle = [angle, axis[0], axis[1], axis[2]]
        bpy.data.materials[f'Cone({_ix},{_iy},{_iz})'].node_tree.nodes[1].inputs[0].default_value = [color[0], color[1], color[2], 1]
        bpy.data.materials[f'Cone({_ix},{_iy},{_iz})'].node_tree.nodes[1].inputs[0].keyframe_insert(data_path='default_value', frame=i*time_dilation_factor)
        object.keyframe_insert(data_path='rotation_axis_angle', frame=i*time_dilation_factor)
        object.rotation_axis_angle = [0, 0, 0, 0]
