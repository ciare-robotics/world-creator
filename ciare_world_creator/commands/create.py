import json
import os
import re
import sys
import uuid

import click
import openai
import questionary
from click import pass_context
from tinydb import Query, TinyDB

from ciare_world_creator.collections.utils import get_or_create_collection
from ciare_world_creator.contexts_prompts.model import fmt_model_qa_tmpl
from ciare_world_creator.contexts_prompts.world import fmt_world_qa_tmpl
from ciare_world_creator.model_databases.fetch_worlds import download_world
from ciare_world_creator.model_databases.gazebo import GazeboLoader
from ciare_world_creator.model_databases.objaverse import ObjaverseLoader
from ciare_world_creator.sim_interfaces.gazebo import GazeboSimInterface
from ciare_world_creator.sim_interfaces.mujoco import MujocoSimInterface
from ciare_world_creator.utils.cache import Cache
from ciare_world_creator.utils.json import NumpyEncoder
from ciare_world_creator.utils.style import STYLE
from ciare_world_creator.xml.worlds import find_model


@click.command(
    "create",
    short_help="Create new simulation world",
)
@pass_context
def cli(ctx):
    cache = Cache()
    db = TinyDB(os.path.join(cache.worlds_path, "world_db.json"))

    from ciare_world_creator.llm.model import prompt_model

    simulators = ["mujoco", "gazebo"]
    chosen_simulator = questionary.select(
        message=("Choose simulator to generate world for."),
        choices=simulators,
        style=STYLE,
    ).ask()

    chosen_model = "gpt-4-turbo"  # Gpt-4 is default and cheapest
    if chosen_simulator == "gazebo":
        # Only gazebo is supported
        loader = GazeboLoader()
        interface = GazeboSimInterface(chosen_model)
    elif chosen_simulator == "mujoco":
        loader = ObjaverseLoader()
        interface = MujocoSimInterface(chosen_model)
    models, worlds = loader.get_models()

    world_query = questionary.text(
        "Enter query for world generation(E.g Two cars and person next to it)",
        style=STYLE,
    ).ask()

    if not world_query:
        sys.exit(os.EX_OK)

    query = world_query.lower()
    query = query.replace("\n", "")

    World = Query()
    exists = db.search(World.prompt == query)

    if exists:
        questionary.print(
            f"World already exists at {exists[0]['filepath']}... 🦄",
            style="bold italic fg:green",
        )
        # return

    model_collection = get_or_create_collection("models_" + chosen_simulator, loader)
    try:
        claim_query_result = model_collection.query(
            query_texts=[query],
            include=["documents", "distances", "metadatas"],
            n_results=20,
        )

    except openai.error.AuthenticationError:
        questionary.print(
            f"OpenAI api key at {cache.cache_path}/openai_api_key incorrect. "
            "Regenerate it at https://platform.openai.com/account/api-keys at copy "
            f"to {cache.cache_path}/openai_api_key",
            style="bold italic fg:red",
        )
        sys.exit(os.EX_DATAERR)

    context = [
        {"name": name, "metadata": metadata}
        for name, metadata in zip(
            claim_query_result["documents"][0], claim_query_result["metadatas"][0]
        )
    ]
    generate_world = False  # Pretty unstable, disabled for now

    if generate_world:
        content = fmt_world_qa_tmpl.format(context_str=worlds)

        questionary.print("Generating world... 🌎", style="bold fg:yellow")
        world = prompt_model(content, query, chosen_model)

        questionary.print(
            f"World is {world['World']}, downloading it", style="bold italic fg:green"
        )

        full_world = interface.find_world(world["World"], worlds)
        template_world_path = None
        if world["World"] != "None":
            template_world_path = download_world(
                world["World"], full_world["owner"], cache.worlds_path
            )

        if not template_world_path:
            questionary.print(
                "There was error in download world. Falling back to empty world",
                style="bold italic fg:red",
            )
            template_world_path = os.path.join(cache.worlds_path, "empty.sdf")
    else:
        template_world_path = os.path.join(cache.worlds_path, "empty.sdf")

    questionary.print(
        "Selecting models from database... 🫖", style="bold italic fg:yellow"
    )
    content = fmt_model_qa_tmpl.format(context_str=context)
    chosen_models = prompt_model(content, query, chosen_model)

    # Some models are hallucinated
    filtered_models = []
    for model in chosen_models:
        if find_model(model["Model"], models):
            filtered_models.append(model)
    chosen_models = filtered_models

    questionary.print(
        f"Placing {len(chosen_models)} models in the world... 📍",
        style="bold italic fg:yellow",
    )
    cleaned_query = re.sub(r'[<>:;.,"/\\|?*]', "", query).strip()
    world_name = f'world_{cleaned_query.replace(" ", "_")}'
    world_path = (
        os.path.join(cache.worlds_path, world_name) + interface.get_world_extension()
    )

    saved_models = interface.add_models(
        chosen_models, loader.get_models_full(), query, world_path, template_world_path
    )

    db.insert(
        {
            "id": str(uuid.uuid4()),
            "name": world_name,
            "filepath": world_path,
            "prompt": query,
            "total_models": json.dumps(saved_models, cls=NumpyEncoder),
            "world_name": "Empty",
        }
    )

    questionary.print(
        f"Finished! Output available at { world_path } 🦄",
        style="bold italic fg:green",
    )
