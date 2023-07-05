import os
import sys

import click
import questionary
from click import pass_context
from tinydb import Query, TinyDB

from ciare_world_creator.model_databases.gazebo import GazeboLoader
from ciare_world_creator.utils.cache import Cache
from ciare_world_creator.utils.style import STYLE
from ciare_world_creator.xml.worlds import add_model_to_xml, find_model, save_xml


@click.command(
    "fix",
    short_help="Sometimes, world downloaded can be malformed, so we will take all objects spawned by LLM and respawn them in empty world",
)
@pass_context
def cli(ctx):
    cache = Cache()
    db = TinyDB(os.path.join(cache.worlds_path, "world_db.json"))
    loader = GazeboLoader()
    full_models = loader.get_models_full()

    all_names = [d["name"] for d in db.all()]
    name = questionary.autocomplete(
        "Enter world name", choices=all_names, style=STYLE
    ).ask()
    if not name:
        sys.exit(os.EX_OK)

    name = name.strip()

    World = Query()
    exists = db.search(World.name == name)
    if not exists:
        questionary.print(
            f"World {name} not exists in db... Run ciare_world_creator list to view available worlds 🦄",
            style="bold italic fg:green",
        )
        return

    exists = exists[0]
    xml_file = exists["filepath"]

    include_elements = []
    i = 0
    for model in exists["total_models"]:
        # Example usage
        m = find_model(model["Model"], full_models)

        include = add_model_to_xml(
            m["name"] + str(i),
            model["Pose"]["x"],
            model["Pose"]["y"],
            model["Pose"]["z"],
            0,
            0,
            0,
            f"https://fuel.gazebosim.org/1.0/{m['owner']}/models/{m['name'].replace(' ', '%20')}",
        )
        include_elements.append(include)
        i = i + 1

    template_world_path = os.path.join(cache.worlds_path, "empty.sdf")

    save_xml(exists["filepath"], template_world_path, include_elements)

    questionary.print(
        f'Finished! Output available at {exists["filepath"]} 🦄',
        style="bold italic fg:green",
    )
