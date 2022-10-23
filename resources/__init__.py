bl_info = {
    "name" : "NPR Shader",
    "blender" : (3,2,2),
    "category" : "Material",
    "version" : (1,0,0),
    "author" : "Kent Edoloverio",
    "description" : "Add Non-photo realistic Shader to your Meshes"
    }

import bpy
import os
from bpy.types import Panel, Operator


ADDON_PATH = os.path.dirname(__file__)

def import_from_library(library):
    path = os.path.join(ADDON_PATH, library + '.blend')
    with bpy.data.libraries.load(path) as (data_from, data_to):
        data_to.node_groups = [x for x in data_from.node_groups if not x in bpy.data.node_groups]

    for datablock in data_to.node_groups:
        datablock.use_fake_user = True

class NPRShader(Operator):
    bl_idname = "material.append_npr_nodes"
    bl_label = "Add NPR Shader"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self,context):
        import_from_library('npr_shader');
        return {'FINISHED'}

class Outline(Operator):
    bl_idname = "material.append_outline"
    bl_label = "Add Outline"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        # Solidify Modifier
        bpy.ops.object.modifier_add(type='SOLIDIFY')
        bpy.context.object.modifiers["Solidify"].thickness = 0.02
        bpy.context.object.modifiers["Solidify"].offset = -1
        bpy.context.object.modifiers["Solidify"].use_rim = False
        bpy.context.object.modifiers["Solidify"].use_flip_normals = True
        bpy.context.object.modifiers["Solidify"].use_quality_normals = True
        bpy.context.object.modifiers["Solidify"].material_offset = 1

        # Outline Material Shader
        bpy.ops.object.material_slot_add()
        outline_material = bpy.data.materials.new(name='NPR Outline')
        outline_material.use_nodes = True
        outline_material.use_backface_culling = True

        outline_material.node_tree.nodes.remove(outline_material.node_tree.nodes.get('Principled BSDF'))
        material_output = outline_material.node_tree.nodes.get('Material Output')
        diffuse = outline_material.node_tree.nodes.new('ShaderNodeBsdfDiffuse')

        diffuse.inputs['Color'].default_value = (0, 0, 0, 1) #last value alpha

        # link diffuse shader to material
        outline_material.node_tree.links.new(material_output.inputs[0], diffuse.outputs[0])
        # set activer material to your new material
        bpy.context.object.active_material = outline_material
        return {'FINISHED'}


class ShaderPanel(Panel):
    bl_idname = 'VIEW3D_PT_example_panel'
    bl_label = 'NPR SHADER'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator("material.append_npr_nodes")
        col.operator("material.append_outline")


def register():
    bpy.utils.register_class(ShaderPanel)
    bpy.utils.register_class(NPRShader)
    bpy.utils.register_class(Outline)


def unregister():
    bpy.utils.unregister_class(ShaderPanel)
    bpy.utils.unregister_class(NPRShader)
    bpy.utils.unregister_class(Outline)
