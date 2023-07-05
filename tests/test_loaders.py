import json
import unittest
from unittest import mock

from ciare_world_creator.model_databases.gazebo import GazeboLoader
from ciare_world_creator.utils.cache import Cache


class TestGazeboLoader(unittest.TestCase):
    def setUp(self):
        self.loader = GazeboLoader()
        self.loader.cache.model_db_file = "models.json"
        self.loader.cache.world_db_file = "worlds.json"

    def tearDown(self):
        self.loader = None

    @mock.patch("builtins.open")
    def test_get_models_full(self, mock_open):
        read_data = json.dumps({"model1": "data1", "model2": "data2"})
        mock_open = mock.mock_open(read_data=read_data)

        with mock.patch("builtins.open", mock_open):
            models = self.loader.get_models_full()

        mock_open.assert_called_once_with("models.json", "r")
        self.assertEqual(models, {"model1": "data1", "model2": "data2"})

    def test_get_worlds_full(self):
        read_data = json.dumps({"world1": "data1", "world2": "data2"})
        mock_open = mock.mock_open(read_data=read_data)

        with mock.patch("builtins.open", mock_open):
            worlds = self.loader.get_worlds_full()

        mock_open.assert_called_once_with("worlds.json", "r")
        self.assertEqual(worlds, {"world1": "data1", "world2": "data2"})

    def test_get_models(self):
        model_data = json.dumps(
            [
                {
                    "name": "test",
                    "tags": ["auv"],
                    "categories": ["Robots", "Science and Technology"],
                },
                {
                    "name": "test2",
                    "tags": ["test_tag"],
                    "categories": ["Robots", "Art"],
                },
                {"name": "test3", "tags": ["robot"], "categories": ["Fun"]},
            ]
        )
        worlds_data = json.dumps(
            [
                {
                    "name": "testWorld",
                    "tags": ["auv"],
                    "categories": ["Robots", "Science and Technology"],
                },
                {
                    "name": "testWorld2",
                    "tags": ["test_tag"],
                    "categories": ["Robots", "Art"],
                },
                {"name": "testWorld3", "tags": ["robot"], "categories": ["Fun"]},
            ]
        )

        mock_files = [
            mock.mock_open(read_data=content).return_value
            for content in [model_data, worlds_data]
        ]
        mock_opener = mock.mock_open()
        mock_opener.side_effect = mock_files

        with mock.patch("builtins.open", mock_opener):
            only_description_models, only_description_worlds = self.loader.get_models()

        self.assertEqual(len(mock_opener.call_args_list), 2)

        expected_models = [
            {
                "name": "test",
                "tags": ["auv"],
                "categories": ["Robots", "Science and Technology"],
            },
            {"name": "test2", "tags": ["test_tag"], "categories": ["Robots", "Art"]},
            {"name": "test3", "tags": ["robot"], "categories": ["Fun"]},
        ]
        self.assertEqual(only_description_models, expected_models)

        expected_worlds = [
            {
                "name": "testWorld",
                "tags": ["auv"],
                "categories": ["Robots", "Science and Technology"],
            },
            {
                "name": "testWorld2",
                "tags": ["test_tag"],
                "categories": ["Robots", "Art"],
            },
            {"name": "testWorld3", "tags": ["robot"], "categories": ["Fun"]},
        ]
        self.assertEqual(only_description_worlds, expected_worlds)


if __name__ == "__main__":
    unittest.main()
