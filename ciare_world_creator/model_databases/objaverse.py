import json
import os

import objaverse

from ciare_world_creator.model_databases.base import BaseLoader
from ciare_world_creator.utils.cache import Cache


class ObjaverseLoader(BaseLoader):
    def __init__(self):
        cache = Cache()
        print("Downloading objaverse annotations...")
        fp = os.path.join(cache.cache_path, "LVIS.json")
        if os.path.exists(fp):
            # If the file does not exist, create it and dump the JSON data
            with open(fp, "r") as file:
                cached = json.load(file)
                self.annotations = cached[0]
                self.uid_to_category = cached[1]
            return

        lvis_annotations = objaverse.load_lvis_annotations()

        truncated_annotations = (
            {}
        )  # Only take 3 annotations from each of the category, we don't need more
        for key, value_list in lvis_annotations.items():
            truncated_annotations[key] = value_list[:3]

        self.uid_to_category = {}
        for key, value_list in truncated_annotations.items():
            for item in value_list:
                self.uid_to_category[item] = key

        self.annotations = objaverse.load_annotations(self.uid_to_category.keys())
        with open(fp, "w") as file:
            json.dump([self.annotations, self.uid_to_category], file)

    def get_models_full(self):
        return self.get_models()[0]

    def get_models(self):
        only_description_models = []

        for uuid, category in self.uid_to_category.items():
            only_description_models.append(
                {
                    "uuid": uuid,
                    "name": self.annotations[uuid]["name"],
                    "categories": [category],
                    "tags": [tag["name"] for tag in self.annotations[uuid]["tags"]],
                }
            )

        return only_description_models, None
