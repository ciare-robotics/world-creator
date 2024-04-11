from typing import Dict, List

import questionary
from lxml import etree
from lxml import etree as ET

from ciare_world_creator.sim_interfaces.base import BaseSimInterface
from ciare_world_creator.xml.worlds import find_model


class GazeboSimInterface(BaseSimInterface):
    def __init__(self, chosen_model: str) -> None:
        super().__init__(chosen_model)
        self.dataset = "fuel-gazebo"

    def check_world(self, template_world_path):
        """Load world and asserts if basic tags are there."""
        parser = ET.XMLParser(recover=True, remove_blank_text=True)

        tree = etree.parse(template_world_path, parser=parser)

        root = tree.getroot()
        world_xml = root.find("world")
        return world_xml is not None

    def get_world_extension(self) -> str:
        return ".sdf"

    def place_models(self, models: List[Dict], placed_models: List[Dict]) -> List[Dict]:
        updated_models = models
        for i, model in enumerate(placed_models):
            updated_models[i].update(model)
        return updated_models

    def add_models(
        self,
        chosen_models: List[Dict],
        models: List[Dict],
        query: str,
        path_to_save: str,
        world_template_path: str,
    ) -> List[Dict]:
        placed_models = self.prompt_model_for_placement(chosen_models, query)
        non_existent_models = []
        include_elements = []
        i = 0
        for model in placed_models:
            # Example usage
            m = find_model(model["Model"], models)
            if not m:
                questionary.print(
                    f"Model {model} was not found in database. "
                    "LLM hallucinated and made that up, skipping this model...",
                    style="bold italic fg:red",
                )
                non_existent_models.append(model)
                i = i + 1
                continue

            include = self.add_model_to_xml(
                m["name"] + str(i),
                model["Pose"]["x"],
                model["Pose"]["y"],
                model["Pose"]["z"],
                0,
                0,
                0,
                "https://fuel.gazebosim.org/1.0/"
                f"{m['owner']}/models/{m['name'].replace(' ', '%20')}",
            )
            include_elements.append(include)
            i = i + 1

        self.save_xml(path_to_save, world_template_path, include_elements)
        return placed_models

    def add_model_to_xml(
        self, model_name, pose_x, pose_y, pose_z, pose_roll, pose_pitch, pose_yaw, uri
    ):
        # Create the new <include> element
        include = ET.Element("include")

        name = ET.SubElement(include, "name")
        name.text = model_name

        pose = ET.SubElement(include, "pose")
        pose.text = f"{pose_x} {pose_y} {pose_z} {pose_roll} {pose_pitch} {pose_yaw}"

        uri_element = ET.SubElement(include, "uri")
        uri_element.text = uri

        return include

    def save_xml(self, xml_file, template_world_path, include_tags):
        parser = ET.XMLParser(recover=True, remove_blank_text=True)

        tree = etree.parse(template_world_path, parser=parser)

        root = tree.getroot()

        world_xml = root.find("world")

        for include in include_tags:
            world_xml.append(include)

        # Indent the XML with two spaces
        tree_str = ET.tostring(
            root,
            pretty_print=True,
            encoding="utf-8",
            xml_declaration=True,
            with_tail=True,
        )

        # parsed_tree = ET.fromstring(tree_str)

        # Save the formatted XML to the file
        with open(xml_file, "wb") as file:
            file.write(tree_str)
