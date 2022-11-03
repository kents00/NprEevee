bl_info = {
    "name" : "NPR Shader",
    "blender" : (3,2,2),
    "category" : "Material",
    "version" : (1,2,1),
    "author" : "Kent Edoloverio",
    "description" : "Add Non-photo realistic Shader to your Meshes"
    }

import bpy
from bpy.types import Panel, Operator


# THIS IS THE LATEST VERSION OF THIS ADDON; INSTALL THE LATEST VERSION ON THE FOLDER "RELEASE"

class NPR_Shader(Operator):
    bl_idname = "material.append_npr_nodes"
    bl_label  = "Add NPR Shader"

    def create_group(self,context):
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

        #Input
        group_input = npr_group.nodes.new("NodeGroupInput")
        group_input.location = (174, 71)
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

        #Output
        group_output = npr_group.nodes.new("NodeGroupOutput")
        group_output.location = (269, 90)
        npr_group.outputs.new('NodeSocketColor','Color')

        #Diffuse BSDF
        diffuse_bsdf = npr_group.nodes.new(type = "ShaderNodeBsdfDiffuse")
        diffuse_bsdf.location = (120,128)

        #Shader To RGB
        shaderto_rgb_1 = npr_group.nodes.new(type = "ShaderNodeShaderToRGB")
        shaderto_rgb_1.location = (196, 139)

        #Separate Color
        separate_color = npr_group.nodes.new(type = "ShaderNodeSeparateColor")
        separate_color.location = (282, 129)




        # KEY LIGHT SECTION

        """Color Ramp"""
        color_ramp_1 = npr_group.nodes.new(type = "ShaderNodeValToRGB")
        color_ramp_1.location = (267, 129)

        color_ramp_1.color_ramp.interpolation = "CONSTANT"

        # Color1
        color_ramp_1.color_ramp.elements.new(0.396)
        color_ramp_1.color_ramp.elements[0].color = (0,0,0,1)

        #Color2
        color_ramp_1.color_ramp.elements.new(0.400)
        color_ramp_1.color_ramp.elements[0].color = (1,1,1,1)

        color_ramp_2 = npr_group.nodes.new(type = "ShaderNodeValToRGB")
        color_ramp_2.location = (280, 34)

        color_ramp_2.color_ramp.interpolation = "CONSTANT"

        # Color1
        color_ramp_2.color_ramp.elements.new(0.396)
        color_ramp_2.color_ramp.elements[0].color = (0,0,0,1)

        #Color2
        color_ramp_2.color_ramp.elements.new(0.400)
        color_ramp_2.color_ramp.elements[0].color = (1,1,1,1)


        color_ramp_3 = npr_group.nodes.new(type = "ShaderNodeValToRGB")
        color_ramp_3.location = (310, 79)

        color_ramp_3.color_ramp.interpolation = "CONSTANT"

        # Color1
        color_ramp_3.color_ramp.elements.new(0.396)
        color_ramp_3.color_ramp.elements[0].color = (0,0,0,1)

        #Color2
        color_ramp_3.color_ramp.elements.new(0.400)
        color_ramp_3.color_ramp.elements[0].color = (1,1,1,1)


        """Mix RGB"""
        mix_rgb_1 = npr_group.nodes.new(type = "ShaderNodeMixRGB")
        mix_rgb_1.location = (294, 113)
        mix_rgb_1.blend_type = 'MULTIPLY'
        mix_rgb_1.inputs[0].default_value = 1

        mix_rgb_2 = npr_group.nodes.new(type = "ShaderNodeMixRGB")
        mix_rgb_2.location = (295, 124)
        mix_rgb_2.blend_type = 'MULTIPLY'
        mix_rgb_2.inputs[0].default_value = 1

        mix_rgb_3 = npr_group.nodes.new(type = "ShaderNodeMixRGB")
        mix_rgb_3.location = (306, 115)
        mix_rgb_3.blend_type = 'MULTIPLY'
        mix_rgb_3.inputs[0].default_value = 1




        # OUTLINE SECTION

        """Color Ramp"""
        color_ramp_4 = npr_group.nodes.new(type = "ShaderNodeValToRGB")
        color_ramp_4.location = (426, 80)

        color_ramp_4.color_ramp.interpolation = "CONSTANT"

        # Color1
        color_ramp_4.color_ramp.elements.new(0.523)
        color_ramp_4.color_ramp.elements[0].color = (1,1,1,1)

        #Color2
        color_ramp_4.color_ramp.elements.new(0.600)
        color_ramp_4.color_ramp.elements[0].color = (0,0,0,1)

        """Math"""
        math_node_1 = npr_group.nodes.new(type = "ShaderNodeMath")
        math_node_1.location = (197, 121)
        math_node_1.operation = "POWER"

        math_node_2 = npr_group.nodes.new(type = "ShaderNodeMath")
        math_node_2.location = (257, 107)
        math_node_2.operation = "MULTIPLY"

        math_node_3 = npr_group.nodes.new(type = "ShaderNodeMath")
        math_node_3.location = (273, 113)
        math_node_3.operation = "ADD"

        math_node_4 = npr_group.nodes.new(type = "ShaderNodeMath")
        math_node_4.location = (245, 139)
        math_node_4.operation = "MULTIPLY"

        """Layer Weight"""
        layer_weight_1 = npr_group.nodes.new(type = "ShaderNodeLayerWeight")
        layer_weight_1.location = (321,123)





        # SPECULAR SECTION

        """Color Ramp"""

        color_ramp_5 = npr_group.nodes.new(type = "ShaderNodeValToRGB")
        color_ramp_5.location = (335, 136)

        color_ramp_1.color_ramp.interpolation = "LINEAR"

        # Color1
        color_ramp_5.color_ramp.elements.new(0.018)
        color_ramp_5.color_ramp.elements[0].color = (0,0,0,1)

        #Color2
        color_ramp_5.color_ramp.elements.new(0.155)
        color_ramp_5.color_ramp.elements[0].color = (1,1,1,1)

        color_ramp_6 = npr_group.nodes.new(type = "ShaderNodeValToRGB")
        color_ramp_6.location = (285, 55)

        color_ramp_6.color_ramp.interpolation = "LINEAR"

        # Color1
        color_ramp_6.color_ramp.elements.new(0.055)
        color_ramp_6.color_ramp.elements[0].color = (0,0,0,1)

        #Color2
        color_ramp_6.color_ramp.elements.new(0.068)
        color_ramp_6.color_ramp.elements[0].color = (1,1,1,1)


        """Mix RGB"""
        mix_rgb_4 = npr_group.nodes.new(type = "ShaderNodeMixRGB")
        mix_rgb_4.location = (225, 143)
        mix_rgb_4.blend_type = 'MIX'
        # mix_rgb_4.inputs[0] # Fac output is connected to 'Softness' Group Input

        mix_rgb_5 = npr_group.nodes.new(type = "ShaderNodeMixRGB")
        mix_rgb_5.location = (306, 115)
        mix_rgb_5.blend_type = 'MULTIPLY'
        mix_rgb_5.inputs[0].default_value = 1

        """Shader To RGB"""
        shaderto_rgb_2 = npr_group.nodes.new(type = "ShaderNodeShaderToRGB")
        shaderto_rgb_2.location = (367, 117)

        """Specular BDSF"""
        specular_bdsf = npr_group.nodes.new(type = "ShaderNodeEeveeSpecular")
        specular_bdsf.location = (223, 122)

        """Vector Math"""
        vector_math_1 = npr_group.nodes.new(type = "ShaderNodeVectorMath")
        vector_math_1.location = (225, 124)
        vector_math_1.operation = "ADD"

        """Geometry"""
        geometry_1 = npr_group.nodes.new(type = "ShaderNodeNewGeometry")
        geometry_1.location = (238, 143)

        """Combine XYZ"""
        combine_xyz = npr_group.nodes.new(type = "ShaderNodeCombineXYZ")
        combine_xyz.location = (245, 109)



        # BASE SECTION

        """Mix RGB"""
        mix_rgb_6 = npr_group.nodes.new(type = "ShaderNodeMixRGB")
        mix_rgb_6.location = (203, 146)
        mix_rgb_6.blend_type = 'MULTIPLY'
        mix_rgb_6.inputs[0].default_value = 1




        # NEAR KEY LIGHT / BASE SECTION

        """Mix RGB"""
        mix_rgb_7 = npr_group.nodes.new(type = "ShaderNodeMixRGB")
        mix_rgb_7.location = (220, 147)
        mix_rgb_7.blend_type = 'LIGHTEN'
        mix_rgb_7.inputs[0].default_value = 1

        mix_rgb_8 = npr_group.nodes.new(type = "ShaderNodeMixRGB")
        mix_rgb_8.location = (328, 136)
        mix_rgb_8.blend_type = 'ADD'
        mix_rgb_8.inputs[0].default_value = 1
        # mix_rgb_9.inputs[1]
        # mix_rgb_9.inputs[2] # This will be connected to mix shader specular section

        mix_rgb_9 = npr_group.nodes.new(type = "ShaderNodeMixRGB")
        mix_rgb_9.location = (379, 129)
        mix_rgb_9.blend_type = 'ADD'
        mix_rgb_9.inputs[0].default_value = 1

        # mix_rgb_9.inputs[1]
        # mix_rgb_9.inputs[0] # Fac output is connected to Key Light 'Color Ramp' Output


        mix_rgb_10 = npr_group.nodes.new(type = "ShaderNodeMixRGB")
        mix_rgb_10.location = (379, 129)
        mix_rgb_10.blend_type = 'MIX'
        # mix_rgb_10.inputs[0] # Fac output is connected to Outline SECTION 'Color Ramp' Output

        # The output color of this mix rgb will be inserted to "NodeGroupOutput"
        mix_rgb_11 = npr_group.nodes.new(type = "ShaderNodeMixRGB")
        mix_rgb_11.location = (316, 149)
        mix_rgb_11.blend_type = 'ADD'
        mix_rgb_11.inputs[0].default_value = 1




        # CONNECTING NODES

        link = npr_group.links.new

        # DIFFUSE SECTION
        link(diffuse_bsdf.outputs[0], shaderto_rgb_1.inputs[0])
        link(shaderto_rgb_1.outputs[0], separate_color.inputs[0])

            # KEY LIGHT SECTION
        link(separate_color.outputs[0], color_ramp_1.inputs[0])
        link(separate_color.outputs[1], color_ramp_2.inputs[0])
        link(separate_color.outputs[2], color_ramp_3.inputs[0])

        link(color_ramp_1.outputs[0], mix_rgb_1.inputs[1])
        link(color_ramp_2.outputs[0], mix_rgb_2.inputs[1])
        link(color_ramp_3.outputs[0], mix_rgb_3.inputs[1])

        link(mix_rgb_1.inputs[2], group_input.outputs[2])
        link(mix_rgb_2.inputs[2], group_input.outputs[3])
        link(mix_rgb_3.inputs[2], group_input.outputs[4])

        # OUTLINE SECTION
        link(color_ramp_4.outputs[0], mix_rgb_11.inputs[0])
        link(math_node_1.outputs[0], color_ramp_4.inputs[0])
        link(layer_weight_1.outputs[0], math_node_1.inputs[0])
        link(math_node_2.outputs[0], math_node_1.inputs[1])
        link(separate_color.outputs[1], math_node_2.inputs[0])
        link(math_node_3.outputs[0], math_node_2.inputs[1])
        link(group_input.outputs[7], math_node_3.inputs[1])
        link(math_node_4.outputs[0], math_node_3.inputs[0])
        link(group_input.outputs[8], math_node_4.inputs[0])
        link(group_input.outputs[6], math_node_4.inputs[1])

        # SPECULAR SECTION
        link(mix_rgb_5.outputs[0], mix_rgb_9.inputs[2])
        link(mix_rgb_4.outputs[0], mix_rgb_5.inputs[1])
        link(group_input.outputs[10], mix_rgb_4.inputs[0])
        link(color_ramp_5.outputs[0], mix_rgb_4.inputs[1])
        link(color_ramp_6.outputs[0], mix_rgb_4.inputs[2])
        link(shaderto_rgb_2.outputs[0], color_ramp_5.inputs[0])
        link(shaderto_rgb_2.outputs[0], color_ramp_6.inputs[0])
        link(specular_bdsf.outputs[0], shaderto_rgb_2.inputs[0])
        link(vector_math_1.outputs[0], specular_bdsf.inputs[5])
        link(geometry_1.outputs[1], vector_math_1.inputs[0])
        link(combine_xyz.outputs[0], vector_math_1.inputs[1])
        link(group_input.outputs[11], combine_xyz.inputs[0])
        link(group_input.outputs[12], combine_xyz.inputs[1])
        link(group_input.outputs[13], combine_xyz.inputs[2])

            # NEAR KEY LIGHT / BASE COLOR
        link(mix_rgb_7.outputs[0], mix_rgb_6.inputs[1])
        link(group_input.outputs[1], mix_rgb_7.inputs[2])
        link(group_input.outputs[0], mix_rgb_6.inputs[2])
        link(mix_rgb_6.outputs[0], mix_rgb_8.inputs[1])
        link(group_input.outputs[8], mix_rgb_8.inputs[2])
        link(mix_rgb_8.outputs[0], mix_rgb_9.inputs[1])
        link(mix_rgb_5.outputs[0], mix_rgb_9.inputs[2])
        link(mix_rgb_9.outputs[0], mix_rgb_10.inputs[2])
        link(group_input.outputs[5], mix_rgb_10.inputs[1])
        link(color_ramp_4.outputs[0], mix_rgb_10.inputs[0])
        link(mix_rgb_10.outputs[0], mix_rgb_11.inputs[1])
        link(mix_rgb_3.outputs[0], mix_rgb_11.inputs[2])
        link(mix_rgb_11.outputs[0], group_output.inputs[0])

        # Add Node Group into Node Editor
        tree = bpy.context.object.active_material.node_tree
        group_node = tree.nodes.new("ShaderNodeGroup")
        group_node.node_tree = npr_group
        group_node.location = (-40, 300)
        group_node.use_custom_color = True
        group_node.color = (1, 0.341, 0.034)
        group_node.width = 250

        shader_node_output_material_node = tree.nodes["Material Output"]
        links = tree.links
        links.new(group_node.outputs[0], shader_node_output_material_node.inputs[0])

    def execute(self, context):
        self.create_group(context)
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



def register():
    bpy.utils.register_class(NPR_Shader)
    bpy.utils.register_class(Outline)
    bpy.utils.register_class(ShaderPanel)



def unregister():
    bpy.utils.unregister_class(NPR_Shader)
    bpy.utils.unregister_class(Outline)
    bpy.utils.register_class(ShaderPanel)


if __name__ == "__main__":
    register()