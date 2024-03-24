import os
from pathlib import Path

import objaverse
import trimesh
from obj2mjcf.cli import Args, process_obj


class MujocoSimInterface:
    def __init__(self):
        pass

    def check_world(self, world):
        pass

    def generate_world(self):
        world = {"World": "None"}
        template_world_path = os.path.join(cache.worlds_path, "empty.sdf")

    def find_entry_by_name(self, name, full_list):
        for entry in full_list:
            if entry["name"] == name:
                return entry
        return None

    def add_models(self, placed_models, models):
        full_placed_models = []

        for model in placed_models:
            if model_entry := self.find_entry_by_name(model["Model"], models):
                model_entry.update(model)
                full_placed_models.append(model_entry)
                print(model_entry)
        print(full_placed_models)

        # model_db_interface.load_models(full_placed_models)
        objects = objaverse.load_objects(
            uids=[entry["uuid"] for entry in full_placed_models]
        )
        obj_locs = list(objects.values())

        print(obj_locs)

        for i in range(len(full_placed_models)):
            full_placed_models[i]["model_loc"] = obj_locs[i]

            mesh = trimesh.load(obj_locs[i])
            # trimesh.exchange.obj.export_obj(mesh)
            obj, data = trimesh.exchange.export.export_obj(
                mesh, include_texture=True, return_texture=True
            )

            obj_path = f"./converted/{full_placed_models[i]['uuid']}.obj"
            with open(obj_path, "w") as f:
                f.write(obj)
            # save the MTL and images
            for k, v in data.items():
                with open(os.path.join("./converted/", k), "wb") as f:
                    f.write(v)
            args = Args("./", save_mjcf=True, compile_model=True, overwrite=True)

            process_obj(Path(obj_path), args)
