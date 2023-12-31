import datetime
import os
import zipfile
import io
import json
import webbrowser
import requests
import shutil
import bpy
from bpy.types import Panel, Operator

bl_info = {
    "name": "NPR Shader",
    "blender": (4, 0, 2),
    "category": "3D View",
    "location": "3D View > NPR Shader",
    "version": (3, 0, 0),
    "author": "Kent Edoloverio",
    "description": "Add Non-photo realistic Shader to your Meshes",
    "wiki_url": "",
    "tracker_url": "",
}


class GithubEngine:
    def __init__(self):
        self._api_url = 'https://api.github.com'
        self._token = None
        self._user = None
        self._repo = None
        self._current_version = None
        self._latest_version = None
        self._response = None
        self._update_date = None

    def clear_state(self):
        self._token = None
        self._user = None
        self._repo = None
        self._current_version = None
        self._latest_version = None
        self._response = None
        self._update_date = None

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        if value is None:
            self._token = None
        else:
            self._token = str(value)

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        self._user = str(value)

    @property
    def repo(self):
        return self._repo

    @repo.setter
    def repo(self, value):
        self._repo = str(value)

    @property
    def api_url(self):
        return self._api_url

    @property
    def update_date(self):
        return self._update_date

    @api_url.setter
    def api_url(self, value):
        if not self.check_is_url(value):
            raise ValueError("Not a valid URL: " + value)
        self._api_url = value

    @staticmethod
    def check_is_url(url):
        if not ("http://" in url or "https://" in url):
            return False
        if "." not in url:
            return False
        return True

    def delete_file_in_folder(self):
        """
        The function `delete_file_in_folder` deletes all files inside a specified folder.
        """
        folder_path = os.path.join(
            os.path.dirname(__file__), "..", f"{self.repo}")

        directories = [item for item in os.listdir(
            folder_path) if os.path.isdir(os.path.join(folder_path, item))]

        try:
            for directory_name in directories:
                if directory_name.startswith(f"{self.user}"):
                    target_folder = os.path.join(folder_path, directory_name)
                    for root, dirs, files in os.walk(target_folder):
                        for file in files:
                            file_path = os.path.join(root, file)
                            if file == "version_info.json":
                                os.remove(file_path)

            print(f"Files inside {folder_path} deleted successfully.")
        except FileNotFoundError as e:
            print(f"Error deleting files in {folder_path}: {e}")

    def delete_folder(self):
        """
        The `delete_folder` function deletes a specific folder and its contents within a given
        repository.
        """
        folder_path = os.path.join(
            os.path.dirname(__file__), "..", f"{self.repo}")

        directories = [item for item in os.listdir(
            folder_path) if os.path.isdir(os.path.join(folder_path, item))]
        try:
            for directory_name in directories:
                if directory_name.startswith(f"{self.user}"):
                    target_folder = os.path.join(folder_path, directory_name)
                    shutil.rmtree(target_folder)
            print(f"Folder {folder_path} deleted successfully.")
        except FileNotFoundError as e:
            print(f"Error deleting folder {folder_path}: {e}")

    def extract_folder(self):
        """
        The function `extract_folder` extracts the contents of a specific folder from a given repository
        and copies them to the base path.
        """
        folder_path = os.path.join(
            os.path.dirname(__file__), "..", f"{self.repo}")
        directories = [item for item in os.listdir(
            folder_path) if os.path.isdir(os.path.join(folder_path, item))]
        # Find the specific folder that starts with username
        target_folder = None
        for directory_name in directories:
            if directory_name.startswith(f"{self.user}"):
                target_folder = os.path.join(folder_path, directory_name)
                break

        if target_folder is not None:
            destination_folder = folder_path
            print(f"Found target folder: {target_folder}")
            for item in os.listdir(target_folder):
                source_item_path = os.path.join(target_folder, item)
                destination_item_path = os.path.join(destination_folder, item)

                if os.path.isfile(source_item_path):
                    shutil.copy2(source_item_path, destination_item_path)
                elif os.path.isdir(source_item_path):
                    shutil.copytree(source_item_path, destination_item_path)
            print("Contents extracted to base path.")
        else:
            print("Target folder not found.")

    @bpy.app.handlers.persistent
    def check_for_updates(self):
        """
        The above function checks for updates of a Blender add-on by making a request to a specified API
        endpoint and compares the latest version with the current version of the add-on.
        :return: The code is returning the latest version of the addon, the current version of the
        addon, and the update date.
        """
        update_url = f"{self.api_url}/repos/{self.user}/{self.repo}/releases/latest"
        addon_path = os.path.dirname(__file__)

        try:
            response = requests.get(update_url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print("Error checking for updates:", e)
            if response.status_code != 200:
                print("Response content:", response.content)
            return None

        data = json.loads(response.text)
        date = datetime.datetime.now()
        latest_version = data["tag_name"]
        current_version = f"{bl_info['version'][0]}.{bl_info['version'][1]}.{bl_info['version'][2]}"

        addon_version = {
            "current_version": current_version,
            "latest_version": latest_version,
            "update_date": str(date),
        }
        json_file_path = os.path.join(addon_path, "version_info.json")
        try:
            with open(json_file_path, 'w') as json_file:
                json.dump(addon_version, json_file, indent=1)
        except zipfile.BadZipFile as e:
            print("Error extracting zip file:", e)
            return None
        if self._latest_version != self._current_version:
            return self._latest_version
        return self._current_version, self._update_date

    @bpy.app.handlers.persistent
    def update(self):
        """
        The `update` function downloads a zip file from a specified URL, extracts its contents, and
        performs some additional operations on the extracted files.
        :return: None if there is an error extracting the zip file.
        """
        zipball_url = f"{self.api_url}/repos/{self.user}/{self.repo}/zipball/{self.check_for_updates()}"

        response = requests.get(zipball_url)
        self._response = response

        addon_path = os.path.dirname(__file__)
        zip_data = io.BytesIO(response.content)

        try:
            with zipfile.ZipFile(zip_data, 'r') as zip_ref:
                zip_ref.extractall(addon_path)
                self.extract_folder()
                self.delete_file_in_folder()
                self.delete_folder()
        except zipfile.BadZipFile as e:
            print("Error extracting zip file:", e)
            return None


engine = GithubEngine()


class NPR_Shader(Operator):
    bl_idname = "material.append_npr_nodes"
    bl_label = "Add NPR Shader"

    def __init__(self):
        self.source_file = os.path.join(os.path.dirname(
            __file__), "..", "NprEevee/data", "NprShader.blend")

    def import_file(self):
        if not os.path.isfile(self.source_file):
            self.report(
                {'ERROR'}, "File not found: {}".format(self.source_file))
        return {'FINISHED'}

    def create_node_group(self, context):
        bpy.ops.object.material_slot_add()
        npr_material = bpy.data.materials.new(name='NPR Shader')
        npr_material.use_nodes = True
        npr_material.node_tree.nodes.remove(
            npr_material.node_tree.nodes.get('Principled BSDF'))
        mesh = context.object.data
        mesh.materials.clear()
        mesh.materials.append(npr_material)

        for mat in bpy.data.materials:
            if "TestMat" in mat.name:
                nodes = mat.node_tree.nodes
                for node in nodes:
                    if node.type != 'OUTPUT_MATERIAL':  # skip the material output node as we'll need it later
                        nodes.remove(node)

        npr_group = bpy.data.node_groups.new(
            type="ShaderNodeTree", name="NPR Shader")

        # setup nodes inside the group
        group_in = npr_group.nodes.new("NodeGroupInput")
        group_in.location = (-1250, 350)
        npr_group.inputs.new('NodeSocketColor', 'Base Color')
        npr_group.inputs.new('NodeSocketColor', 'Shadow Color')
        npr_group.inputs.new('NodeSocketColor', 'Key Light Color')
        npr_group.inputs.new('NodeSocketColor', 'Fill Light Color')
        npr_group.inputs.new('NodeSocketColor', 'Back Light Color')
        npr_group.inputs.new('NodeSocketColor', 'Outline Color')
        npr_group.inputs.new('NodeSocketFloatFactor', 'Outline Minus')
        npr_group.inputs.new('NodeSocketFloatFactor', 'Outline Size')
        npr_group.inputs.new('NodeSocketFloatFactor', 'Outline Mask')
        npr_group.inputs.new('NodeSocketColor', 'Specular Color')
        npr_group.inputs.new('NodeSocketFloatFactor', 'Softness')
        npr_group.inputs.new('NodeSocketFloatFactor', 'Offset X')
        npr_group.inputs.new('NodeSocketFloatFactor', 'Offset Y')
        npr_group.inputs.new('NodeSocketFloatFactor', 'Offset Z')

        groupin_keylight = npr_group.nodes.new("NodeGroupInput")
        groupin_keylight.location = (-600, -600)

        group_out = npr_group.nodes.new("NodeGroupOutput")
        group_out.location = (650, 400)
        npr_group.outputs.new('NodeSocketColor', 'Color')

        # CONNECTING NODES
        link = npr_group.links.new

        # Diffuse BSDF
        diffuse_bsdf = npr_group.nodes.new(type="ShaderNodeBsdfDiffuse")
        diffuse_bsdf.location = (-950, -350)

        # Shader To RGB
        shaderto_rgb_1 = npr_group.nodes.new(type="ShaderNodeShaderToRGB")
        shaderto_rgb_1.location = (-700, -400)

        # Separate Color
        separate_color = npr_group.nodes.new(type="ShaderNodeSeparateColor")
        separate_color.location = (-500, -400)

        # KEY LIGHT SECTION

        """Color Ramp"""
        color_ramp_1 = npr_group.nodes.new(type="ShaderNodeValToRGB")
        color_ramp_1.location = (-300, -150)

        color_ramp_1.color_ramp.interpolation = "CONSTANT"

        # Color1
        color_ramp_1.color_ramp.elements.new(0.400)
        color_ramp_1.color_ramp.elements[1].color = (1, 1, 1, 1)

        # Color2
        color_ramp_1.color_ramp.elements.new(0.396)
        color_ramp_1.color_ramp.elements[0].color = (0, 0, 0, 1)

        color_ramp_1.color_ramp.elements.remove(
            color_ramp_1.color_ramp.elements[0])
        color_ramp_1.color_ramp.elements.remove(
            color_ramp_1.color_ramp.elements[2])

        color_ramp_2 = npr_group.nodes.new(type="ShaderNodeValToRGB")
        color_ramp_2.location = (-300, -450)

        color_ramp_2.color_ramp.interpolation = "CONSTANT"

        # Color1
        color_ramp_2.color_ramp.elements.new(0.900)
        color_ramp_2.color_ramp.elements[1].color = (1, 1, 1, 1)

        # Color2
        color_ramp_2.color_ramp.elements.new(0.899)
        color_ramp_2.color_ramp.elements[0].color = (0, 0, 0, 1)

        color_ramp_2.color_ramp.elements.remove(
            color_ramp_2.color_ramp.elements[0])
        color_ramp_2.color_ramp.elements.remove(
            color_ramp_2.color_ramp.elements[2])

        color_ramp_3 = npr_group.nodes.new(type="ShaderNodeValToRGB")
        color_ramp_3.location = (-300, -750)

        color_ramp_3.color_ramp.interpolation = "CONSTANT"

        # Color1
        color_ramp_3.color_ramp.elements.new(0.400)
        color_ramp_3.color_ramp.elements[1].color = (1, 1, 1, 1)

        # Color2
        color_ramp_3.color_ramp.elements.new(0.388)
        color_ramp_3.color_ramp.elements[0].color = (0, 0, 0, 1)

        color_ramp_3.color_ramp.elements.remove(
            color_ramp_3.color_ramp.elements[0])
        color_ramp_3.color_ramp.elements.remove(
            color_ramp_3.color_ramp.elements[2])

        """MIX RGB"""
        mix_rgb_1 = npr_group.nodes.new(type="ShaderNodeMixRGB")
        mix_rgb_1.location = (0, -150)
        mix_rgb_1.blend_type = 'MULTIPLY'
        mix_rgb_1.inputs[0].default_value = 1

        mix_rgb_2 = npr_group.nodes.new(type="ShaderNodeMixRGB")
        mix_rgb_2.location = (0, -450)
        mix_rgb_2.blend_type = 'MULTIPLY'
        mix_rgb_2.inputs[0].default_value = 1

        mix_rgb_3 = npr_group.nodes.new(type="ShaderNodeMixRGB")
        mix_rgb_3.location = (0, -750)
        mix_rgb_3.blend_type = 'MULTIPLY'
        mix_rgb_3.inputs[0].default_value = 1

        # OUTLINE SECTION
        color_ramp_4 = npr_group.nodes.new(type="ShaderNodeValToRGB")
        color_ramp_4.location = (-300, 700)

        color_ramp_4.color_ramp.interpolation = "CONSTANT"

        # Color1
        color_ramp_4.color_ramp.elements.new(0.600)
        color_ramp_4.color_ramp.elements[0].color = (0, 0, 0, 1)

        # Color2
        color_ramp_4.color_ramp.elements.new(0.599)
        color_ramp_4.color_ramp.elements[1].color = (1, 1, 1, 1)

        color_ramp_4.color_ramp.elements.remove(
            color_ramp_4.color_ramp.elements[0])
        color_ramp_4.color_ramp.elements.remove(
            color_ramp_4.color_ramp.elements[2])

        """Math"""
        math_node_1 = npr_group.nodes.new(type="ShaderNodeMath")
        math_node_1.location = (-500, 700)
        math_node_1.operation = "POWER"

        math_node_2 = npr_group.nodes.new(type="ShaderNodeMath")
        math_node_2.location = (-700, 700)
        math_node_2.operation = "MULTIPLY"

        math_node_3 = npr_group.nodes.new(type="ShaderNodeMath")
        math_node_3.location = (-900, 700)
        math_node_3.operation = "ADD"

        math_node_4 = npr_group.nodes.new(type="ShaderNodeMath")
        math_node_4.location = (-1100, 700)
        math_node_4.operation = "MULTIPLY"

        """Layer Weight"""
        layer_weight_1 = npr_group.nodes.new(type="ShaderNodeLayerWeight")
        layer_weight_1.location = (-700, 900)
        layer_weight_1.inputs[0].default_value = 0.5

        # SPECULAR SECTION
        color_ramp_5 = npr_group.nodes.new(type="ShaderNodeValToRGB")
        color_ramp_5.location = (-300, 2000)

        color_ramp_5.color_ramp.interpolation = "CONSTANT"

        # Color1
        color_ramp_5.color_ramp.elements.new(0.090)
        color_ramp_5.color_ramp.elements[0].color = (0, 0, 0, 1)

        # Color2
        color_ramp_5.color_ramp.elements.new(0.100)
        color_ramp_5.color_ramp.elements[1].color = (1, 1, 1, 1)

        color_ramp_5.color_ramp.elements.remove(
            color_ramp_5.color_ramp.elements[0])
        color_ramp_5.color_ramp.elements.remove(
            color_ramp_5.color_ramp.elements[2])

        color_ramp_6 = npr_group.nodes.new(type="ShaderNodeValToRGB")
        color_ramp_6.location = (-300, 1700)

        color_ramp_6.color_ramp.interpolation = "CONSTANT"

        # Color1
        color_ramp_6.color_ramp.elements.new(0.090)
        color_ramp_6.color_ramp.elements[0].color = (0, 0, 0, 1)

        # Color2
        color_ramp_6.color_ramp.elements.new(0.100)
        color_ramp_6.color_ramp.elements[1].color = (1, 1, 1, 1)

        color_ramp_6.color_ramp.elements.remove(
            color_ramp_6.color_ramp.elements[0])
        color_ramp_6.color_ramp.elements.remove(
            color_ramp_6.color_ramp.elements[2])

        """Mix RGB"""
        mix_rgb_4 = npr_group.nodes.new(type="ShaderNodeMixRGB")
        mix_rgb_4.location = (450, 1800)
        mix_rgb_4.blend_type = 'MULTIPLY'
        mix_rgb_4.inputs[0].default_value = 1
        # mix_rgb_4.inputs[0] # Fac output is connected to 'Softness' Group Input

        mix_rgb_5 = npr_group.nodes.new(type="ShaderNodeMixRGB")
        mix_rgb_5.location = (100, 1800)
        mix_rgb_5.blend_type = 'MIX'

        """Shader To RGB"""
        shaderto_rgb_2 = npr_group.nodes.new(type="ShaderNodeShaderToRGB")
        shaderto_rgb_2.location = (-550, 2000)

        """Specular BDSF"""
        specular_bdsf = npr_group.nodes.new(type="ShaderNodeEeveeSpecular")
        specular_bdsf.location = (-750, 2000)

        """Vector Math"""
        vector_math_1 = npr_group.nodes.new(type="ShaderNodeVectorMath")
        vector_math_1.location = (-950, 2000)
        vector_math_1.operation = "ADD"

        """Geometry"""
        geometry_1 = npr_group.nodes.new(type="ShaderNodeNewGeometry")
        geometry_1.location = (-1250, 2000)

        """Combine XYZ"""
        combine_xyz = npr_group.nodes.new(type="ShaderNodeCombineXYZ")
        combine_xyz.location = (-1550, 2000)

        # NEAR LIGHT / BASE SECTION

        """Mix RGB"""
        mix_rgb_7 = npr_group.nodes.new(type="ShaderNodeMixRGB")
        mix_rgb_7.location = (350, -200)
        mix_rgb_7.blend_type = 'LIGHTEN'
        mix_rgb_7.inputs[0].default_value = 1

        mix_rgb_8 = npr_group.nodes.new(type="ShaderNodeMixRGB")
        mix_rgb_8.location = (450, -250)
        mix_rgb_8.blend_type = 'MULTIPLY'
        mix_rgb_8.inputs[0].default_value = 1

        mix_rgb_9 = npr_group.nodes.new(type="ShaderNodeMixRGB")
        mix_rgb_9.location = (650, -350)
        mix_rgb_9.blend_type = 'ADD'
        mix_rgb_9.inputs[0].default_value = 1

        mix_rgb_10 = npr_group.nodes.new(type="ShaderNodeMixRGB")
        mix_rgb_10.location = (850, -550)
        mix_rgb_10.blend_type = 'ADD'
        mix_rgb_10.inputs[0].default_value = 1

        mix_rgb_11 = npr_group.nodes.new(type="ShaderNodeMixRGB")
        mix_rgb_11.location = (1050, -650)
        mix_rgb_11.blend_type = 'MIX'
        mix_rgb_11.inputs[0].default_value = 1

        mix_rgb_12 = npr_group.nodes.new(type="ShaderNodeMixRGB")
        mix_rgb_12.location = (1150, -750)
        mix_rgb_12.blend_type = 'ADD'
        mix_rgb_12.inputs[0].default_value = 1

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
        group_node.color = (0, 0, 0)
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
        links.new(group_node.outputs[0],
                  shader_node_output_material_node.inputs[0])

    def import_node_group(self, node_group_name):
        with bpy.data.libraries.load(self.source_file, link=False) as (data_from, data_to):
            if node_group_name in data_from.node_groups:
                data_to.node_groups = [node_group_name]

        if not data_to.node_groups or not data_to.node_groups[0]:
            self.report(
                {'ERROR'}, "Failed to load the node group: {}".format(node_group_name))
            self.report(
                {'INFO'}, "Creating new node group: {}".format(node_group_name))
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
        group_node.color = (0, 0, 0)
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
            links.new(
                group_node.outputs[0], shader_node_output_material_node.inputs[0])

        self.report(
            {'INFO'}, "Successfully appended node group: {}".format(node_group_name))
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

        outline_material.node_tree.nodes.remove(
            outline_material.node_tree.nodes.get('Principled BSDF'))
        material_output = outline_material.node_tree.nodes.get(
            'Material Output')
        diffuse = outline_material.node_tree.nodes.new('ShaderNodeBsdfDiffuse')

        diffuse.inputs['Color'].default_value = (
            0, 0, 0, 1)  # last value alpha
        outline_material.node_tree.links.new(
            material_output.inputs[0], diffuse.outputs[0])
        bpy.context.object.active_material = outline_material
        return {'FINISHED'}


# The `Release_Notes` class is an operator in Blender that opens the release notes of an addon in a
# web browser.
class Release_Notes(bpy.types.Operator):
    bl_label = "View the Release Notes"
    bl_idname = "addonupdater.release_notes"

    def execute(self, context):
        webbrowser.open(
            f"https://github.com/{engine.user}/{engine.repo}", new=1)
        return {'FINISHED'}


# The above class is an operator in Blender that checks for updates to an add-on and updates it if a
# new version is available.
class Update(bpy.types.Operator):
    bl_label = "Update"
    bl_idname = "addonupdater.checkupdate"

    @classmethod
    def poll(cls, context):
        return engine._current_version != engine._latest_version

    def execute(self, context):
        engine.update()
        if engine._response.status_code != 200:
            self.report({'ERROR'}, "Error getting update")
            return {'CANCELLED'}

        if engine._current_version == engine._latest_version:
            self.report(
                {'ERROR'}, "You are already using the latest version of the add-on.")
            return {'CANCELLED'}

        self.report(
            {'INFO'}, "Add-on has been updated. Please restart Blender to apply changes.")
        return {'FINISHED'}


# The Check_for_update class is a Blender operator that checks for updates to an add-on and reports if
# a new version is available.
class Check_for_update(bpy.types.Operator):
    bl_label = "Check Update"
    bl_idname = "addonupdater.update"

    def invoke(self, context, event):
        self.execute(self)
        return {'FINISHED'}

    def execute(self, context):
        engine.check_for_updates()
        if not engine.user or not engine.repo:
            self.report(
                {'ERROR'}, "GitHub user and repository details are not set.")
            return {'CANCELLED'}
        if engine._current_version != engine._latest_version:
            self.report({'INFO'}, "A new version is available!")
        elif engine._current_version == engine._latest_version:
            self.report(
                {'INFO'}, "You are already using the latest version of the add-on.")
        return {'FINISHED'}


# The above class is an addon preferences class in Python that displays information about the latest
# version of the addon and provides options to check for updates and update the addon.
class AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row()
        row.scale_y = 2
        row.operator("addonupdater.release_notes", icon="HELP")
        row = box.row()
        row.scale_y = 2
        row.operator(Check_for_update.bl_idname, icon="TRIA_DOWN_BAR")
        row.scale_y = 2
        row.alert = True
        row.operator(Update.bl_idname, icon="FILE_REFRESH")

        json_file_path = os.path.join(
            os.path.dirname(__file__), "version_info.json")

        try:
            with open(json_file_path, 'r') as json_file:
                version_info = json.load(json_file)
                engine._update_date = version_info.get("update_date")
                engine._latest_version = version_info.get("latest_version")
                engine._current_version = version_info.get("current_version")

                if engine._latest_version is not None:
                    row = box.row()
                    row.label(
                        text=f"Version: {engine._latest_version}")
                elif engine._current_version == engine._latest_version:
                    row = box.row()
                    row.label(
                        text=f"You are using the latest version: {engine._latest_version}")
                if engine._update_date is not None:
                    row = box.row()
                    row.label(text=f"Last update: {engine._update_date}")
        except json.decoder.JSONDecodeError as e:
            print(f"Error loading JSON file: {e}")
            row = box.row()
            row.label(text="Last update: Never")
        except FileNotFoundError:
            row = box.row()
            row.label(text="Error loading version information.")


class ShaderPanel(Panel):
    bl_label = "NPR Shader"
    bl_idname = "npr_shader.panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS' if bpy.app.version < (2, 80) else 'UI'
    bl_category = "NPR Shader"

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
    AddonPreferences,
    NPR_Shader,
    Outline,
    ShaderPanel,
    Release_Notes,
    Check_for_update,
    Update,
)


def register():

    engine.user = "kents00"  # Replace this with your username
    engine.repo = "NprEevee"  # Replace this with your repository name

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    engine.clear_state()
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
