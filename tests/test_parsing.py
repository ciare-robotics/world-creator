import pytest

from ciare_world_creator.utils.json import parse_output_to_json


@pytest.fixture
def output_fixture():
    output = '''"content": "```json\n[{\n    \"Model\": \"hatchback_2\",\n    \"Pose\": {\n        \"x\": 0.5,\n        \"y\": 0,\n        \"z\": 0\n    }\n},\n{\n    \"Model\": \"SUV\",\n    \"Pose\": {\n        \"x\": -0.5,\n        \"y\": 0,\n        \"z\": 0\n    }\n},\n{\n    \"Model\": \"Casual female\",\n    \"Pose\": {\n        \"x\": 0,\n        \"y\": 0,\n        \"z\": 0\n    }\n}]\n```"'''
    return output


def test_parse_output_to_json(output_fixture):
    expected_json = [
        {"Model": "hatchback_2", "Pose": {"x": 0.5, "y": 0, "z": 0}},
        {"Model": "SUV", "Pose": {"x": -0.5, "y": 0, "z": 0}},
        {"Model": "Casual female", "Pose": {"x": 0, "y": 0, "z": 0}},
    ]

    parsed_json = parse_output_to_json(output_fixture)
    assert parsed_json == expected_json
