import bpy
import numpy as np
import time

root = '/home/pdmurray/Desktop/Workspace/simtoblender/'
datadir = 'bloch_nucleation_mx.out/'
nframes = 100
scaling = 5e7
step = 101
radius = .15
length = .3
vertices = 32
time_dilation_factor = 1 # Must be int

def generate_cones():
    
    t0 = time.time()
    print('Generating cones...')
    
    for m in bpy.data.meshes:
        bpy.data.meshes.remove(m)
    
    for m in bpy.data.materials:
        bpy.data.materials.remove(m)
        
    for m in bpy.data.objects:
        bpy.data.objects.remove(m)

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
        
    # Generate a new cone mesh. 
    bpy.ops.mesh.primitive_cone_add(vertices=vertices,radius1=radius,radius2=0.0,depth=length,location=(0, 0, 0))
    master_cone = bpy.context.active_object
    master_cone.rotation_mode = 'AXIS_ANGLE'
    scene = bpy.context.scene

    # Make a new cone object for each location. The name of the cones should include the indices, i.e., Cone(ix,iy,iz).
    for i, (_ix, _iy, _iz, _x, _y, _z) in enumerate(zip(ix, iy, iz, x, y, z)):
        object = master_cone.copy()
        object.data = master_cone.data.copy()
        object.location = (_x, _y, _z)
        object.name = f'Cone({_ix},{_iy},{_iz})'
        new_mat = bpy.data.materials.new(name=f'Cone({_ix},{_iy},{_iz})')
        new_mat.use_nodes = True
        object.data.materials.append(new_mat)
        scene.collection.objects.link(object)

    bpy.data.objects.remove(master_cone)        
    print(f'Cones generated in {time.time() - t0} s.')
    
    return

def get_colors_and_lut():
    
    t0 = time.time()
    print('Getting colors and lut...')
    
    data_values = []
    for i in range(nframes):
        with open(root + datadir + f'rodrigues{i:06d}.csv', 'r') as f:
            lines = f.readlines()
            
        i_start = 0
        while lines[i_start][0] == '#':
            i_start += 1
        
        for line in lines[i_start:]:
            s = line.split(',')
            data_values.append(float(s[-1]))
            
    min_div_m = np.min(data_values)
    max_div_m = np.max(data_values)
    
    # Generate new colors/materials which span the color space
    with open(root + 'colors.csv', 'r') as f:
        lines = f.readlines()
    colors = np.array([list(map(float, line.split())) for line in lines])
    datalut = np.linspace(min_div_m, max_div_m, len(colors))        
    
    print(f'Colors and lut found in {time.time()-t0} s.')
    
    return colors, datalut

def generate_keyframes(colors, datalut):
    
    t0 = time.time()
    print(f'Generating keyframes...')
    
    for ob in bpy.data.objects:
        ob.animation_data_clear()
    
    # Rotate and keyframe for each Rodrigues file
    for i in range(nframes):
        
        print(f'Frame {i:06d}/{nframes:06d}', end='\r')
        
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
            
        for _ix, _iy, _iz, axis, angle, _div in list(zip(ix, iy, iz, axes, angles, div)):#[::step]:
            color = colors[int(len(colors)*(np.max(datalut) - _div)/(np.max(datalut)-np.min(datalut)))]
            object = bpy.data.objects[f'Cone({_ix},{_iy},{_iz})']
            object.rotation_axis_angle = [angle, axis[0], axis[1], axis[2]]
            bpy.data.materials[f'Cone({_ix},{_iy},{_iz})'].node_tree.nodes[1].inputs[0].default_value = [color[0], color[1], color[2], 1]
            bpy.data.materials[f'Cone({_ix},{_iy},{_iz})'].node_tree.nodes[1].inputs[0].keyframe_insert(data_path='default_value', frame=i*time_dilation_factor)
            object.keyframe_insert(data_path='rotation_axis_angle', frame=i*time_dilation_factor)
            object.rotation_axis_angle = [0, 0, 0, 0]
            
    
    print(f'Keyframes generated in {time.time()-t0} s.')
            
    return


#generate_cones()
colors, lut = get_colors_and_lut()
generate_keyframes(colors, lut)
