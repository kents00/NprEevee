bl_info = {
    "name" : "NPR Shader",
    "blender" : (3,5,1),
    "category" : "3D View",
    "location" : "3D View > NPR Shader",
    "version" : (2,8,1),
    "author" : "Kent Edoloverio",
    "description" : "Add Non-photo realistic Shader to your Meshes",
    "wiki_url" : "",
    "tracker_url" : "",
    }

import bpy
import os
from bpy.types import Panel, Operator

class NPR_Shader(Operator):
    bl_idname = "material.append_npr_nodes"
    bl_label  = "Add NPR Shader"

    def __init__(self):
        self.source_file = os.path.join(os.path.dirname(__file__), "..", "NprEevee/data", "NprShader.blend")

    def import_file(self):
        if not os.path.isfile(self.source_file):
            self.report({'ERROR'}, "File not found: {}".format(self.source_file))
        return {'FINISHED'}

    def create_node_group(self,context):
        bpy.ops.object.material_slot_add()
        npr_material = bpy.data.materials.new(name='NPR Shader')
        npr_material.use_nodes = True
        npr_material.node_tree.nodes.remove(npr_material.node_tree.nodes.get('Principled BSDF'))
        mesh = context.object.data
        mesh.materials.clear()
        mesh.materials.append(npr_material)

        for mat in bpy.data.materials:
            if "TestMat" in mat.name:
                nodes = mat.node_tree.nodes
                for node in nodes:
                    if node.type != 'OUTPUT_MATERIAL':  # skip the material output node as we'll need it later
                        nodes.remove(node)

        npr_group = bpy.data.node_groups.new(type = "ShaderNodeTree", name = "NPR Shader")

        # setup nodes inside the group
        group_in = npr_group.nodes.new("NodeGroupInput")
        group_in.location = (-1250,350)
        npr_group.inputs.new('NodeSocketColor','Base Color')
        npr_group.inputs.new('NodeSocketColor','Shadow Color')
        npr_group.inputs.new('NodeSocketColor','Key Light Color')
        npr_group.inputs.new('NodeSocketColor','Fill Light Color')
        npr_group.inputs.new('NodeSocketColor','Back Light Color')
        npr_group.inputs.new('NodeSocketColor','Outline Color')
        npr_group.inputs.new('NodeSocketFloatFactor','Outline Minus')
        npr_group.inputs.new('NodeSocketFloatFactor','Outline Size')
        npr_group.inputs.new('NodeSocketFloatFactor','Outline Mask')
        npr_group.inputs.new('NodeSocketColor','Specular Color')
        npr_group.inputs.new('NodeSocketFloatFactor','Softness')
        npr_group.inputs.new('NodeSocketFloatFactor','Offset X')
        npr_group.inputs.new('NodeSocketFloatFactor','Offset Y')
        npr_group.inputs.new('NodeSocketFloatFactor','Offset Z')


        groupin_keylight = npr_group.nodes.new("NodeGroupInput")
        groupin_keylight.location = (-600, -600)


        group_out = npr_group.nodes.new("NodeGroupOutput")
        group_out.location = (650,400)
        npr_group.outputs.new('NodeSocketColor','Color')

        # CONNECTING NODES
        link = npr_group.links.new

        #Diffuse BSDF
        diffuse_bsdf = npr_group.nodes.new(type = "ShaderNodeBsdfDiffuse")
        diffuse_bsdf.location = (-950,-350)

        #Shader To RGB
        shaderto_rgb_1 = npr_group.nodes.new(type = "ShaderNodeShaderToRGB")
        shaderto_rgb_1.location = (-700, -400)

        #Separate Color
        separate_color = npr_group.nodes.new(type = "ShaderNodeSeparateColor")
        separate_color.location = (-500, -400)

        # KEY LIGHT SECTION

        """Color Ramp"""
        color_ramp_1 = npr_group.nodes.new(type = "ShaderNodeValToRGB")
        color_ramp_1.location = (-300, -150)

        color_ramp_1.color_ramp.interpolation = "CONSTANT"

        #Color1
        color_ramp_1.color_ramp.elements.new(0.400)
        color_ramp_1.color_ramp.elements[1].color = (1,1,1,1)

        # Color2
        color_ramp_1.color_ramp.elements.new(0.396)
        color_ramp_1.color_ramp.elements[0].color = (0,0,0,1)

        color_ramp_1.color_ramp.elements.remove( color_ramp_1.color_ramp.elements[0] )
        color_ramp_1.color_ramp.elements.remove( color_ramp_1.color_ramp.elements[2] )


        color_ramp_2 = npr_group.nodes.new(type = "ShaderNodeValToRGB")
        color_ramp_2.location = (-300, -450)

        color_ramp_2.color_ramp.interpolation = "CONSTANT"

        #Color1
        color_ramp_2.color_ramp.elements.new(0.900)
        color_ramp_2.color_ramp.elements[1].color = (1,1,1,1)

        # Color2
        color_ramp_2.color_ramp.elements.new(0.899)
        color_ramp_2.color_ramp.elements[0].color = (0,0,0,1)

        color_ramp_2.color_ramp.elements.remove( color_ramp_2.color_ramp.elements[0] )
        color_ramp_2.color_ramp.elements.remove( color_ramp_2.color_ramp.elements[2] )


        color_ramp_3 = npr_group.nodes.new(type = "ShaderNodeValToRGB")
        color_ramp_3.location = (-300, -750)

        color_ramp_3.color_ramp.interpolation = "CONSTANT"

        #Color1
        color_ramp_3.color_ramp.elements.new(0.400)
        color_ramp_3.color_ramp.elements[1].color = (1,1,1,1)

        # Color2
        color_ramp_3.color_ramp.elements.new(0.388)
        color_ramp_3.color_ramp.elements[0].color = (0,0,0,1)

        color_ramp_3.color_ramp.elements.remove( color_ramp_3.color_ramp.elements[0] )
        color_ramp_3.color_ramp.elements.remove( color_ramp_3.color_ramp.elements[2] )

        """MIX RGB"""
        mix_rgb_1 = npr_group.nodes.new(type = "ShaderNodeMixRGB")
        mix_rgb_1.location = (0, -150)
        mix_rgb_1.blend_type = 'MULTIPLY'
        mix_rgb_1.inputs[0].default_value = 1

        mix_rgb_2 = npr_group.nodes.new(type = "ShaderNodeMixRGB")
        mix_rgb_2.location = (0, -450)
        mix_rgb_2.blend_type = 'MULTIPLY'
        mix_rgb_2.inputs[0].default_value = 1

        mix_rgb_3 = npr_group.nodes.new(type = "ShaderNodeMixRGB")
        mix_rgb_3.location = (0, -750)
        mix_rgb_3.blend_type = 'MULTIPLY'
        mix_rgb_3.inputs[0].default_value = 1




        #OUTLINE SECTION
        color_ramp_4 = npr_group.nodes.new(type = "ShaderNodeValToRGB")
        color_ramp_4.location = (-300, 700)

        color_ramp_4.color_ramp.interpolation = "CONSTANT"

        #Color1
        color_ramp_4.color_ramp.elements.new(0.600)
        color_ramp_4.color_ramp.elements[0].color = (0,0,0,1)

        # Color2
        color_ramp_4.color_ramp.elements.new(0.599)
        color_ramp_4.color_ramp.elements[1].color = (1,1,1,1)

        color_ramp_4.color_ramp.elements.remove( color_ramp_4.color_ramp.elements[0] )
        color_ramp_4.color_ramp.elements.remove( color_ramp_4.color_ramp.elements[2] )


        """Math"""
        math_node_1 = npr_group.nodes.new(type = "ShaderNodeMath")
        math_node_1.location = (-500, 700)
        math_node_1.operation = "POWER"

        math_node_2 = npr_group.nodes.new(type = "ShaderNodeMath")
        math_node_2.location = (-700, 700)
        math_node_2.operation = "MULTIPLY"

        math_node_3 = npr_group.nodes.new(type = "ShaderNodeMath")
        math_node_3.location = (-900, 700)
        math_node_3.operation = "ADD"

        math_node_4 = npr_group.nodes.new(type = "ShaderNodeMath")
        math_node_4.location = (-1100, 700)
        math_node_4.operation = "MULTIPLY"

        """Layer Weight"""
        layer_weight_1 = npr_group.nodes.new(type = "ShaderNodeLayerWeight")
        layer_weight_1.location = (-700,900)
        layer_weight_1.inputs[0].default_value = 0.5



        # SPECULAR SECTION
        color_ramp_5 = npr_group.nodes.new(type = "ShaderNodeValToRGB")
        color_ramp_5.location = (-300, 2000)

        color_ramp_5.color_ramp.interpolation = "CONSTANT"

        #Color1
        color_ramp_5.color_ramp.elements.new(0.090)
        color_ramp_5.color_ramp.elements[0].color = (0,0,0,1)

        # Color2
        color_ramp_5.color_ramp.elements.new(0.100)
        color_ramp_5.color_ramp.elements[1].color = (1,1,1,1)

        color_ramp_5.color_ramp.elements.remove( color_ramp_5.color_ramp.elements[0] )
        color_ramp_5.color_ramp.elements.remove( color_ramp_5.color_ramp.elements[2] )

        color_ramp_6 = npr_group.nodes.new(type = "ShaderNodeValToRGB")
        color_ramp_6.location = (-300, 1700)

        color_ramp_6.color_ramp.interpolation = "CONSTANT"

        #Color1
        color_ramp_6.color_ramp.elements.new(0.090)
        color_ramp_6.color_ramp.elements[0].color = (0,0,0,1)

        # Color2
        color_ramp_6.color_ramp.elements.new(0.100)
        color_ramp_6.color_ramp.elements[1].color = (1,1,1,1)

        color_ramp_6.color_ramp.elements.remove( color_ramp_6.color_ramp.elements[0] )
        color_ramp_6.color_ramp.elements.remove( color_ramp_6.color_ramp.elements[2] )

        """Mix RGB"""
        mix_rgb_4 = npr_group.nodes.new(type = "ShaderNodeMixRGB")
        mix_rgb_4.location = (450, 1800)
        mix_rgb_4.blend_type = 'MULTIPLY'
        mix_rgb_4.inputs[0].default_value = 1
        # mix_rgb_4.inputs[0] # Fac output is connected to 'Softness' Group Input

        mix_rgb_5 = npr_group.nodes.new(type = "ShaderNodeMixRGB")
        mix_rgb_5.location = (100, 1800)
        mix_rgb_5.blend_type = 'MIX'


        """Shader To RGB"""
        shaderto_rgb_2 = npr_group.nodes.new(type = "ShaderNodeShaderToRGB")
        shaderto_rgb_2.location = (-550, 2000)

        """Specular BDSF"""
        specular_bdsf = npr_group.nodes.new(type = "ShaderNodeEeveeSpecular")
        specular_bdsf.location = (-750, 2000)

        """Vector Math"""
        vector_math_1 = npr_group.nodes.new(type = "ShaderNodeVectorMath")
        vector_math_1.location = (-950, 2000)
        vector_math_1.operation = "ADD"

        """Geometry"""
        geometry_1 = npr_group.nodes.new(type = "ShaderNodeNewGeometry")
        geometry_1.location = (-1250, 2000)

        """Combine XYZ"""
        combine_xyz = npr_group.nodes.new(type = "ShaderNodeCombineXYZ")
        combine_xyz.location = (-1550, 2000)

        #NEAR LIGHT / BASE SECTION

        """Mix RGB"""
        mix_rgb_7 = npr_group.nodes.new(type = "ShaderNodeMixRGB")
        mix_rgb_7.location = (350, -200)
        mix_rgb_7.blend_type = 'LIGHTEN'
        mix_rgb_7.inputs[0].default_value = 1

        mix_rgb_8 = npr_group.nodes.new(type = "ShaderNodeMixRGB")
        mix_rgb_8.location = (450, -250)
        mix_rgb_8.blend_type = 'MULTIPLY'
        mix_rgb_8.inputs[0].default_value = 1

        mix_rgb_9 = npr_group.nodes.new(type = "ShaderNodeMixRGB")
        mix_rgb_9.location = (650, -350)
        mix_rgb_9.blend_type = 'ADD'
        mix_rgb_9.inputs[0].default_value = 1

        mix_rgb_10 = npr_group.nodes.new(type = "ShaderNodeMixRGB")
        mix_rgb_10.location = (850, -550)
        mix_rgb_10.blend_type = 'ADD'
        mix_rgb_10.inputs[0].default_value = 1

        mix_rgb_11 = npr_group.nodes.new(type = "ShaderNodeMixRGB")
        mix_rgb_11.location = (1050, -650)
        mix_rgb_11.blend_type = 'MIX'
        mix_rgb_11.inputs[0].default_value = 1

        mix_rgb_12 = npr_group.nodes.new(type = "ShaderNodeMixRGB")
        mix_rgb_12.location = (1150, -750)
        mix_rgb_12.blend_type = 'ADD'
        mix_rgb_12.inputs[0].default_value = 1





        #DIFFUSE SECTION
        link(diffuse_bsdf.outputs[0], shaderto_rgb_1.inputs[0])
        link(shaderto_rgb_1.outputs[0], separate_color.inputs[0])

        # KEY LIGHT SECTION
        link(separate_color.outputs[0], color_ramp_1.inputs[0])
        link(separate_color.outputs[1], color_ramp_2.inputs[0])
        link(separate_color.outputs[2], color_ramp_3.inputs[0])

        link(color_ramp_1.outputs[0], mix_rgb_1.inputs[1])
        link(color_ramp_2.outputs[0], mix_rgb_2.inputs[1])
        link(color_ramp_3.outputs[0], mix_rgb_3.inputs[1])

        link(mix_rgb_1.inputs[2], groupin_keylight.outputs[2])
        link(mix_rgb_2.inputs[2], groupin_keylight.outputs[3])
        link(mix_rgb_3.inputs[2], groupin_keylight.outputs[4])

        # OUTLINE SECTION
        # link(color_ramp_4.outputs[0], mix_rgb_11.inputs[0])
        link(math_node_1.outputs[0], color_ramp_4.inputs[0])
        link(layer_weight_1.outputs[0], math_node_1.inputs[0])
        link(math_node_2.outputs[0], math_node_1.inputs[1])
        link(separate_color.outputs[1], math_node_2.inputs[0])
        link(math_node_3.outputs[0], math_node_2.inputs[1])
        link(group_in.outputs[7], math_node_3.inputs[1])
        link(math_node_4.outputs[0], math_node_3.inputs[0])
        link(group_in.outputs[8], math_node_4.inputs[0])
        link(group_in.outputs[6], math_node_4.inputs[1])

        # SPECULAR SECTION
        # link(mix_rgb_5.outputs[0], mix_rgb_9.inputs[2])
        link(mix_rgb_5.outputs[0], mix_rgb_4.inputs[1])
        link(color_ramp_5.outputs[0], mix_rgb_5.inputs[1])
        link(color_ramp_6.outputs[0], mix_rgb_5.inputs[2])
        link(color_ramp_6.outputs[1], mix_rgb_4.inputs[2])

        link(shaderto_rgb_2.outputs[0], color_ramp_5.inputs[0])
        link(shaderto_rgb_2.outputs[0], color_ramp_6.inputs[0])
        link(specular_bdsf.outputs[0], shaderto_rgb_2.inputs[0])
        link(vector_math_1.outputs[0], specular_bdsf.inputs[5])
        link(geometry_1.outputs[1], vector_math_1.inputs[0])
        link(combine_xyz.outputs[0], vector_math_1.inputs[1])
        link(group_in.outputs[9], mix_rgb_4.inputs[2])
        link(group_in.outputs[10], mix_rgb_5.inputs[0])
        link(group_in.outputs[11], combine_xyz.inputs[0])
        link(group_in.outputs[12], combine_xyz.inputs[1])
        link(group_in.outputs[13], combine_xyz.inputs[2])

        # NEAR KEY LIGHT / BASE COLOR
        link(mix_rgb_1.outputs[0], mix_rgb_7.inputs[1])
        link(mix_rgb_7.outputs[0], mix_rgb_8.inputs[1])
        link(mix_rgb_8.outputs[0], mix_rgb_9.inputs[1])
        link(mix_rgb_2.outputs[0], mix_rgb_9.inputs[2])
        link(mix_rgb_9.outputs[0], mix_rgb_10.inputs[1])
        link(mix_rgb_4.outputs[0], mix_rgb_10.inputs[2])
        link(mix_rgb_10.outputs[0], mix_rgb_11.inputs[2])
        link(color_ramp_4.outputs[0], mix_rgb_11.inputs[0])
        link(mix_rgb_11.outputs[0], mix_rgb_12.inputs[1])
        link(mix_rgb_3.outputs[0], mix_rgb_12.inputs[2])

        link(group_in.outputs[5], mix_rgb_11.inputs[1])
        link(group_in.outputs[1], mix_rgb_7.inputs[2])
        link(group_in.outputs[0], mix_rgb_8.inputs[2])

        link(mix_rgb_12.outputs[0], group_out.inputs[0])

        # Add Node Group into Node Editor
        tree = bpy.context.object.active_material.node_tree
        group_node = tree.nodes.new("ShaderNodeGroup")
        group_node.node_tree = npr_group
        group_node.location = (-40, 300)
        group_node.use_custom_color = True
        group_node.color = (0,0,0)
        group_node.inputs[0].default_value = (0.044, 0.034, 0.238, 1)
        group_node.inputs[1].default_value = (0.266, 0.168, 0.753, 1)
        group_node.inputs[2].default_value = (1, 0.275, 0.440, 1)
        group_node.inputs[3].default_value = (1, 0.815, 0.440, 1)
        group_node.inputs[4].default_value = (0.184, 0.056, 0.708, 1)
        group_node.inputs[5].default_value = (0, 0, 0, 1)
        group_node.inputs[6].default_value = 10
        group_node.inputs[7].default_value = 9
        group_node.inputs[8].default_value = 0.5
        group_node.inputs[9].default_value = (0.051, 0.054, 0.098, 1)
        group_node.inputs[10].default_value = 1
        group_node.width = 250

        shader_node_output_material_node = tree.nodes["Material Output"]
        links = tree.links
        links.new(group_node.outputs[0], shader_node_output_material_node.inputs[0])

    def import_node_group(self, node_group_name):
        with bpy.data.libraries.load(self.source_file, link=False) as (data_from, data_to):
            if node_group_name in data_from.node_groups:
                data_to.node_groups = [node_group_name]

        if not data_to.node_groups or not data_to.node_groups[0]:
            self.report({'ERROR'}, "Failed to load the node group: {}".format(node_group_name))
            self.report({'INFO'}, "Creating new node group: {}".format(node_group_name))
            self.create_node_group
            return {'FINISHED'}

        material = bpy.data.materials.new(name=node_group_name)
        material.use_nodes = True
        if bpy.context.object is not None:
            bpy.context.object.data.materials.append(material)

        tree = material.node_tree
        group_node = tree.nodes.new(type='ShaderNodeGroup')
        group_node.node_tree = data_to.node_groups[0]
        group_node.location = (-40, 300)
        group_node.use_custom_color = True
        group_node.color = (0,0,0)
        group_node.inputs[0].default_value = (0.044, 0.034, 0.238, 1)
        group_node.inputs[1].default_value = (0.266, 0.168, 0.753, 1)
        group_node.inputs[2].default_value = (1, 0.275, 0.440, 1)
        group_node.inputs[3].default_value = (1, 0.815, 0.440, 1)
        group_node.inputs[4].default_value = (0.184, 0.056, 0.708, 1)
        group_node.inputs[5].default_value = (0, 0, 0, 1)
        group_node.inputs[6].default_value = 10
        group_node.inputs[7].default_value = 9
        group_node.inputs[8].default_value = 0.5
        group_node.inputs[9].default_value = (0.051, 0.054, 0.098, 1)
        group_node.inputs[10].default_value = 1
        group_node.width = 250

        principled_bsdf_node = tree.nodes.get('Principled BSDF')
        if principled_bsdf_node:
            tree.nodes.remove(principled_bsdf_node)

        shader_node_output_material_node = tree.nodes.get('Material Output')
        if shader_node_output_material_node:
            links = tree.links
            links.new(group_node.outputs[0], shader_node_output_material_node.inputs[0])

        self.report({'INFO'}, "Successfully appended node group: {}".format(node_group_name))
        return {'FINISHED'}

    def execute(self, context):
        self.import_file()
        self.import_node_group("NPREEVEE")
        return {"FINISHED"}


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
        outline_material.node_tree.links.new(material_output.inputs[0], diffuse.outputs[0])
        bpy.context.object.active_material = outline_material
        return {'FINISHED'}

class ShaderPanel(Panel):
    bl_label       = "NPR Shader"
    bl_idname      = "npr_shader.panel"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category    = "NPR Shader"


    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator("material.append_npr_nodes")
        col.operator("material.append_outline")
        col.label(text="SUPPORT ME ON:")
        op = self.layout.operator(
            'wm.url_open',
            text='KO-FI',
            icon='URL'
            )
        op.url = 'https://ko-fi.com/kents_workof_art'


classes = (
    NPR_Shader,
    Outline,
    ShaderPanel
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
