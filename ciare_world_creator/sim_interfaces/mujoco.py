import copy
import os
import shutil
import sys
import xml.etree.ElementTree as ET
from io import StringIO
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import objaverse
import trimesh
from obj2mjcf.cli import Args, process_obj

from ciare_world_creator.sim_interfaces.base import BaseSimInterface
from ciare_world_creator.utils.cache import Cache


class MujocoSimInterface(BaseSimInterface):
    def __init__(self, chosen_model: str) -> None:
        super().__init__(chosen_model)
        self.cache = Cache()

    def check_world(self, world: Dict[str, Union[str, int, float]]) -> None:
        pass

    def generate_world(self) -> str:
        template_world_path = os.path.join(self.cache.worlds_path, "empty.sdf")

        return template_world_path

    def find_entries_by_name(
        self, name: str, full_list: List[Dict]
    ) -> Tuple[List[int], List[Dict]]:
        locs = []
        models = []
        for i, entry in enumerate(full_list):
            if entry["name"] == name:
                locs.append(i)
                models.append(entry)
        return locs, models

    def add_models(
        self,
        chosen_models: List[Dict],
        models: List[Dict],
        query: str,
        path_to_save: str,
        world_path: Optional[str] = None,
    ) -> List[Dict]:
        # Actually methods are badly designed here. TODO is to refactor this.
        full_placed_models = self.get_full_placed_models(chosen_models, models)
        objects = self.load_objects(full_placed_models)
        for i, _ in enumerate(full_placed_models):
            full_placed_models[i]["model_loc"] = objects[full_placed_models[i]["uuid"]]
            full_placed_models[i]["save_fn"] = full_placed_models[i]["uuid"] + f"_{i}"
        full_placed_models = self.update_model_sizes(full_placed_models)

        models_for_scale_prompt = self.format_models_for_scale_prompt(
            full_placed_models
        )
        scaled_models = self.prompt_model_for_scale(models_for_scale_prompt, query)
        full_placed_models = self.scale_models(full_placed_models, scaled_models)
        models_for_placement = self.format_models_for_scale_prompt(full_placed_models)
        placed_models = self.prompt_model_for_placement(models_for_placement, query)
        full_placed_models = self.place_models(full_placed_models, placed_models)
        main_root = self.create_main_root(full_placed_models, objects)
        tree = self.create_tree(main_root)
        self.write_tree_to_file(tree, path_to_save)

        return full_placed_models

    def get_world_extension(self) -> str:
        return ".xml"

    def get_full_placed_models(
        self, placed_models: List[Dict], models: List[Dict]
    ) -> List[Dict]:
        full_placed_models = []
        for model in placed_models:
            locs, model_entries = self.find_entries_by_name(model["Model"], models)
            for model_entry in model_entries:
                model_entry.update(model)
                full_placed_models.append(copy.deepcopy(model_entry))
        return full_placed_models

    def load_objects(self, full_placed_models: List[Dict]) -> Dict[str, str]:
        # TODO abstract dataset loader
        return objaverse.load_objects(
            uids=[entry["uuid"] for entry in full_placed_models]
        )

    def update_model_sizes(self, models: List[Dict]) -> List[Dict]:
        updated_models = models
        for i, model in enumerate(models):
            mesh = trimesh.load(model["model_loc"], force="mesh")
            updated_models[i]["size"] = mesh.extents
        return updated_models

    def format_models_for_scale_prompt(self, models: List[Dict]) -> List[Dict]:
        formatted_models = []
        for model in models:
            formatted_models.append({"Model": model["name"], "Size": model["size"]})
        return formatted_models

    def scale_models(self, models: List[Dict], scaled_models: List[Dict]) -> List[Dict]:
        # Create a dictionary to store unique scales by 'Model'
        unique_scale = {model["Model"]: model for model in scaled_models}
        updated_models = models

        for model in updated_models:
            model["size"] = model["size"] * unique_scale[model["Model"]]["Scale"]
            model["scale"] = unique_scale[model["Model"]]["Scale"]

        return updated_models

    def place_models(self, models: List[Dict], placed_models: List[Dict]) -> List[Dict]:
        updated_models = models
        for i, model in enumerate(placed_models):
            updated_models[i].update(model)
        return updated_models

    def format_models_for_place_prompt(
        self, full_placed_models: List[Dict]
    ) -> List[Dict]:
        models_for_placement = []
        for model in full_placed_models:
            models_for_placement.append({"Model": model["name"], "Size": model["size"]})
        return models_for_placement

    def create_main_root(
        self, full_placed_models: List[Dict], objects: Dict[str, str]
    ) -> ET.Element:
        main_root = ET.Element("mujoco", model="test")
        visual_count = 0
        collision_count = 0
        material_count = 0
        for i, _ in enumerate(full_placed_models):
            material_map = {}

            mesh = self.load_and_scale_mesh(full_placed_models[i])
            obj, data = self.export_mesh(mesh)

            path = self.create_model_path(full_placed_models[i])
            obj_path = self.write_obj_file(obj, path, full_placed_models[i])
            self.save_material_and_images(data, path)
            self.copy_images_to_nested_path(path, full_placed_models[i])
            args = self.create_args(path)
            printed_output = self.process_obj_file(obj_path, args)
            if "Error compiling model" in printed_output:
                print(
                    f"Error compiling model {full_placed_models[i]['Model']},"
                    "it will not be included in final world."
                )
                continue
            saved_mjc_path = self.get_saved_mjc_path(path, full_placed_models[i])
            tree, root, included_tree, included_root = self.parse_xml(saved_mjc_path)

            self.modify_default_class_attributes(
                included_root, material_map, visual_count, collision_count
            )
            visual_count += 1
            collision_count += 1
            self.modify_body_tag(included_root, full_placed_models[i])
            material_count = self.rewrite_material_name_and_references(
                included_root, material_map, material_count
            )
            material_count += 1
            self.write_modified_xml(included_tree, saved_mjc_path)
            self.insert_include_tags(main_root, saved_mjc_path)
        return main_root

    def load_and_scale_mesh(
        self, model: Dict[str, Union[str, int, float]]
    ) -> trimesh.Trimesh:
        mesh = trimesh.load(model["model_loc"], force="mesh")
        mesh.apply_scale(model["scale"])
        return mesh

    def export_mesh(self, mesh: trimesh.Trimesh) -> Tuple[str, Dict[str, bytes]]:
        return trimesh.exchange.export.export_obj(
            mesh, include_texture=True, return_texture=True
        )

    def create_model_path(self, model: Dict[str, Union[str, int, float]]) -> Path:
        path = os.path.join(self.cache.cache_path, f"./converted/{model['save_fn']}")
        path = os.path.abspath(path)
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def write_obj_file(
        self, obj: str, path: Path, model: Dict[str, Union[str, int, float]]
    ) -> str:
        obj_path = f"{path}/{model['save_fn']}.obj"
        with open(obj_path, "w") as f:
            f.write(obj)
        return obj_path

    def save_material_and_images(self, data: Dict[str, bytes], path: Path) -> None:
        for k, v in data.items():
            with open(os.path.join(path, k), "wb") as f:
                f.write(v)

    def copy_images_to_nested_path(
        self, path: Path, model: Dict[str, Union[str, int, float]]
    ) -> None:
        nested_path = Path(os.path.abspath(str(path) + f"/{model['save_fn']}"))
        nested_path.mkdir(parents=True, exist_ok=True)
        files = os.listdir(path)
        for file in files:
            if file.endswith(".png") or file.endswith(".jpg"):
                source_path = os.path.join(path, file)
                destination_path = os.path.join(nested_path, file)
                shutil.copy(source_path, destination_path)

    def create_args(self, path: Path) -> Args:
        return Args(
            obj_dir=path,
            verbose=True,
            save_mjcf=True,
            compile_model=True,
            overwrite=True,
        )

    def process_obj_file(self, obj_path: str, args: Args) -> str:
        sys.stdout = StringIO()
        process_obj(Path(obj_path), args)
        printed_output = sys.stdout.getvalue()
        sys.stdout = sys.__stdout__
        return printed_output

    def get_saved_mjc_path(
        self, path: Path, model: Dict[str, Union[str, int, float]]
    ) -> Path:
        return Path(
            os.path.abspath(
                str(path) + f"/{model['save_fn']}" + f"/{model['save_fn']}.xml"
            )
        )

    def parse_xml(
        self, saved_mjc_path: Path
    ) -> Tuple[ET.ElementTree, ET.Element, ET.ElementTree, ET.Element]:
        tree = ET.parse(saved_mjc_path)
        root = tree.getroot()
        included_tree = ET.parse(saved_mjc_path)
        included_root = included_tree.getroot()
        return tree, root, included_tree, included_root

    def modify_default_class_attributes(
        self,
        included_root: ET.Element,
        material_map: Dict[str, str],
        visual_count: int,
        collision_count: int,
    ) -> None:
        for default in included_root.findall(".//default"):
            class_attribute = default.get("class")
            if class_attribute == "visual":
                material_map[class_attribute] = f"visual{visual_count}"
                default.set("class", material_map[class_attribute])

            elif class_attribute == "collision":
                material_map[class_attribute] = f"collision{visual_count}"
                default.set("class", material_map[class_attribute])

    def modify_body_tag(
        self, included_root: ET.Element, model: Dict[str, Union[str, int, float]]
    ) -> None:
        for body in included_root.findall(".//body"):
            body.set("pos", " ".join(str(e) for e in model["Pose"].values()))
            body.set("euler", "90 0 0")
            ET.SubElement(body, "joint", type="free")

    def rewrite_material_name_and_references(
        self,
        included_root: ET.Element,
        material_map: Dict[str, str],
        material_count: int,
    ) -> int:
        materials = included_root.findall(".//material")
        for i, texture in enumerate(included_root.findall(".//texture")):
            old_name = texture.get("name")
            material_map[old_name] = f"material_{material_count}"
            texture.set("name", material_map[old_name])
            material_count += 1
        for i, material in enumerate(materials):
            old_name = material.get("name")
            if old_name not in material_map:
                material_map[old_name] = f"material_{material_count}"
                material_count += 1
            material.set("name", material_map[old_name])
            texture = material.get("texture")
            if texture:
                material.set("texture", material_map[old_name])
        for i, geom in enumerate(included_root.findall(".//geom")):
            material = geom.get("material")
            if material:
                geom.set("material", material_map[material])
            class_ = geom.get("class")
            if class_:
                geom.set("class", material_map[class_])
        return material_count

    def write_modified_xml(
        self, included_tree: ET.ElementTree, saved_mjc_path: Path
    ) -> None:
        included_tree.write(saved_mjc_path)

    def insert_include_tags(self, main_root: ET.Element, saved_mjc_path: Path) -> None:
        include = ET.SubElement(main_root, "include", file=str(saved_mjc_path))
        include.tail = "\n"

    def create_tree(self, main_root: ET.Element) -> ET.ElementTree:
        tree = ET.ElementTree(main_root)
        env_xml_elements = [ET.Element("asset"), ET.Element("worldbody")]
        self.add_asset_elements(env_xml_elements)
        self.add_worldbody_elements(env_xml_elements)
        main_root.extend(env_xml_elements)
        return tree

    def add_asset_elements(
        self, asset_xml_elements: List[ET.Element]
    ) -> List[ET.Element]:
        asset_elements = [
            ET.SubElement(
                asset_xml_elements[0],
                "texture",
                type="skybox",
                builtin="gradient",
                rgb1=".3 .5 .7",
                rgb2="0 0 0",
                width="32",
                height="512",
            ),
            ET.SubElement(
                asset_xml_elements[0],
                "texture",
                name="body",
                type="cube",
                builtin="flat",
                mark="cross",
                width="128",
                height="128",
                rgb1="0.8 0.6 0.4",
                rgb2="0.8 0.6 0.4",
                markrgb="1 1 1",
                random="0.01",
            ),
            ET.SubElement(
                asset_xml_elements[0],
                "texture",
                name="grid",
                type="2d",
                builtin="checker",
                width="512",
                height="512",
                rgb1=".1 .2 .3",
                rgb2=".2 .3 .4",
            ),
            ET.SubElement(
                asset_xml_elements[0],
                "material",
                name="grid",
                texture="grid",
                texrepeat="1 1",
                texuniform="true",
                reflectance=".2",
            ),
        ]
        for elem in asset_elements:
            elem.tail = "\n"
        return asset_elements

    def add_worldbody_elements(
        self, asset_xml_elements: List[ET.Element]
    ) -> List[ET.Element]:
        worldbody_elements = [
            ET.SubElement(
                asset_xml_elements[1],
                "geom",
                name="floor",
                size="0 0 .05",
                type="plane",
                material="grid",
                condim="3",
            ),
            ET.SubElement(
                asset_xml_elements[1],
                "light",
                castshadow="false",
                pos="0 0 1000",
            ),
        ]
        for elem in worldbody_elements:
            elem.tail = "\n"
        return worldbody_elements

    def write_tree_to_file(self, tree: ET.ElementTree, path: str) -> None:
        tree.write(path, encoding="utf-8", xml_declaration=True)
