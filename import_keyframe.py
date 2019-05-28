import bpy

scn = bpy.context.scene

# Make new material for the input files; edit the material yourself after importing
bpy.ops.material.new()
material = bpy.data.materials[-1]
material.name = 'glyph_material2'
material.use_nodes = True


# Iterate over input files, import each one
for f in range(scn.frame_start, 201):
      
    fpath = bpy.path.abspath('/home/pdmurray/Desktop/Workspace/test_code/sp4.out/sp4.{}.ply'.format(f))
    x = bpy.ops.import_mesh.ply(filepath=fpath)
    obj = bpy.context.selected_objects[0]
    
    # Apply some transforms
    obj.scale = (2e7, 2e7, 2e7)    
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME')
    obj.location = (0, 0, 0)
    
    obj.data.materials.append(material)

    # Keyframe to make it visible only on the current frame
    obj.keyframe_insert('hide',frame=f)
    obj.keyframe_insert('hide_render',frame=f)
    obj.hide = True
    obj.hide_render = True
    obj.keyframe_insert('hide',frame=f-1)
    obj.keyframe_insert('hide_render',frame=f-1)
    obj.keyframe_insert('hide',frame=f+1)
    obj.keyframe_insert('hide_render',frame=f+1)
    
    if f > 201:
        break