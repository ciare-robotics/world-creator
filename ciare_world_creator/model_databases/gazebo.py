import json

from ciare_world_creator.utils.cache import Cache


class GazeboLoader:
    def __init__(self):
        self.cache = Cache()

    def get_models_full(self):
        with open(self.cache.model_db_file, "r") as f:
            models = json.load(f)

        return models

    def get_worlds_full(self):
        with open(self.cache.world_db_file, "r") as f:
            worlds = json.load(f)

        return worlds

    def get_models(self):
        with open(self.cache.model_db_file, "r") as f:
            models = json.load(f)

        with open(self.cache.world_db_file, "r") as f:
            worlds = json.load(f)

        only_description_models = []

        for m in models:
            only_description_models.append(
                {
                    "name": m["name"],
                    "tags": m.get("tags"),
                    "categories": m.get("categories"),
                }
            )

        only_description_worlds = []
        for m in worlds:
            if "subt" in m.get("tags", []):
                continue
            only_description_worlds.append(
                {
                    "name": m["name"],
                    "tags": m.get("tags"),
                    "categories": m.get("categories"),
                }
            )

        return only_description_models, only_description_worlds
