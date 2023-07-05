import asyncio
import os

from ciare_world_creator.model_databases.fetch_models import fetch_models
from ciare_world_creator.model_databases.fetch_worlds import fetch_worlds
from ciare_world_creator.xml.empty_world import empty_world


class Cache:
    def __init__(self, cache: str = None):
        self.cache_path = cache or "/var/tmp/ciare"
        self.worlds_path = os.path.join(self.cache_path, "worlds")
        self.world_db_file = os.path.join(self.cache_path, "gz_worlds.json")
        self.model_db_file = os.path.join(self.cache_path, "gz_models.json")
        if not os.path.exists(self.cache_path):
            os.makedirs(self.cache_path)
        if not os.path.exists(self.worlds_path):
            os.makedirs(self.worlds_path)
        if not os.path.exists(os.path.join(self.worlds_path, "empty.sdf")):
            with open(os.path.join(self.worlds_path, "empty.sdf"), "a+") as f:
                f.write(empty_world())

    def check_api_key(self):
        return os.path.exists(os.path.join(self.cache_path, "openai_api_key"))

    def init_models_and_worlds(self):
        asyncio.run(fetch_models(self.model_db_file))
        asyncio.run(fetch_worlds(self.world_db_file))

    def models_and_worlds_initialized(self):
        return not (
            os.path.exists(self.world_db_file) and os.path.exists(self.model_db_file)
        )
