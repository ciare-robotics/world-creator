from lxml import etree
from lxml import etree as ET


def check_world(template_world_path):
    """Load world and asserts if basic tags are there."""
    parser = ET.XMLParser(recover=True, remove_blank_text=True)

    tree = etree.parse(template_world_path, parser=parser)

    root = tree.getroot()
    world_xml = root.find("world")
    return world_xml is not None


def add_model_to_xml(
    model_name, pose_x, pose_y, pose_z, pose_roll, pose_pitch, pose_yaw, uri
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


def save_xml(xml_file, template_world_path, include_tags):
    parser = ET.XMLParser(recover=True, remove_blank_text=True)

    tree = etree.parse(template_world_path, parser=parser)

    root = tree.getroot()

    world_xml = root.find("world")

    for include in include_tags:
        world_xml.append(include)

    # Indent the XML with two spaces
    tree_str = ET.tostring(
        root, pretty_print=True, encoding="utf-8", xml_declaration=True, with_tail=True
    )

    # parsed_tree = ET.fromstring(tree_str)

    # Save the formatted XML to the file
    with open(xml_file, "wb") as file:
        file.write(tree_str)


def find_model(model, models):
    for m in models:
        if m["name"] == model:
            return m
    return None


def find_world(world, worlds):
    for m in worlds:
        if m["name"] == world:
            return m
    return None
