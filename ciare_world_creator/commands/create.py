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
from ciare_world_creator.contexts_prompts.place import fmt_place_qa_tmpl
from ciare_world_creator.contexts_prompts.world import fmt_world_qa_tmpl
from ciare_world_creator.model_databases.fetch_worlds import download_world
from ciare_world_creator.model_databases.gazebo import GazeboLoader
from ciare_world_creator.utils.cache import Cache
from ciare_world_creator.utils.style import STYLE
from ciare_world_creator.xml.worlds import (
    add_model_to_xml,
    check_world,
    find_model,
    find_world,
    save_xml,
)


@click.command(
    "create",
    short_help="Create new simulation world",
)
@pass_context
def cli(ctx):
    cache = Cache()
    db = TinyDB(os.path.join(cache.worlds_path, "world_db.json"))

    from ciare_world_creator.llm.model import prompt_model

    # Only gazebo is supported
    loader = GazeboLoader()
    full_models = loader.get_models_full()
    full_worlds = loader.get_worlds_full()

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

    openai.api_key = os.getenv("OPENAI_API_KEY")
    models = openai.Model.list()
    allowed_models = ["gpt-3.5-turbo-16k"]
    for model in models["data"]:
        if model["id"] == "gpt-4":
            allowed_models.append("gpt-4")

    if len(allowed_models) > 1:
        chosen_model = questionary.select(
            message="Choose model to generate with. GPT-4 is much better, but also little-bit more expensive",
            choices=allowed_models,
            style=STYLE,
        ).ask()
    else:
        chosen_model = allowed_models[0]

    if exists:
        questionary.print(
            f"World already exists at {exists[0]['filepath']}... 🦄",
            style="bold italic fg:green",
        )
        return

    model_collection = get_or_create_collection("models")
    try:
        claim_query_result = model_collection.query(
            query_texts=[query],
            include=["documents", "distances", "metadatas"],
            n_results=100,
        )
    except openai.error.AuthenticationError:
        questionary.print(
            f"OpenAI api key at {cache.cache_path}/openai_api_key incorrect. Regenerate it at https://platform.openai.com/account/api-keys at copy to {cache.cache_path}/openai_api_key",
            style="bold italic fg:red",
        )
        sys.exit(os.EX_DATAERR)

    context = [
        {"name": name, "metadata": metadata}
        for name, metadata in zip(
            claim_query_result["documents"][0], claim_query_result["metadatas"][0]
        )
    ]

    generate_world = questionary.confirm(
        "Do you want to spawn model in an empty world?"
        "Saying no will download world from database, but it's very unstable. Y/n",
        style=STYLE,
    ).ask()

    if generate_world is None:
        sys.exit(os.EX_OK)

    if not generate_world:
        content = fmt_world_qa_tmpl.format(context_str=worlds)

        questionary.print("Generating world... 🌎", style="bold fg:yellow")
        world = prompt_model(content, query, chosen_model)

        questionary.print(
            f"World is {world['World']}, downloading it", style="bold italic fg:green"
        )

        full_world = find_world(world["World"], full_worlds)
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
        world = {"World": "None"}
        template_world_path = os.path.join(cache.worlds_path, "empty.sdf")

    if not check_world(template_world_path):
        questionary.print(
            "Suggested world is malformed. Falling back to empty world",
            style="bold italic fg:red",
        )
        template_world_path = os.path.join(cache.worlds_path, "empty.sdf")

    questionary.print(
        "Spawning models in the world... 🫖", style="bold italic fg:yellow"
    )
    content = fmt_model_qa_tmpl.format(context_str=context)
    models = prompt_model(content, query, chosen_model)

    for model in models:
        if not find_model(model["Model"], full_models):
            models = prompt_model(
                content,
                f"{model} was not found in context list. Generate only the one that are in the context",
                chosen_model,
            )

    questionary.print("Placing models in the world... 📍", style="bold italic fg:yellow")
    content = fmt_place_qa_tmpl.format(
        context_str=f"Arrange following models: {str(models)}",
        world_file=open(template_world_path, "r"),
    )

    placement = prompt_model(content, query, chosen_model)

    # TODO handle ,.; etc
    cleaned_query = re.sub(r'[<>:;.,"/\\|?*]', "", query).strip()
    world_name = f'world_{cleaned_query.replace(" ", "_")}'

    x, y = 0, 0
    include_elements = []
    i = 0

    # TODO add asserts on model fields
    non_existent_models = []

    for model in placement:
        # Example usage
        m = find_model(model["Model"], full_models)
        if not m:
            questionary.print(
                f"Model {model} was not found in database. LLM hallucinated and made that up, skipping this model...",
                style="bold italic fg:red",
            )
            non_existent_models.append(model)
            i = i + 1
            continue

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

    filtered_models = []
    for model in placement:
        if model not in non_existent_models:
            filtered_models.append(model)

    world_path = os.path.join(cache.worlds_path, f"{world_name}.sdf")

    save_xml(world_path, template_world_path, include_elements)

    if template_world_path != os.path.join(cache.worlds_path, "empty.sdf"):
        os.system(f"rm {template_world_path}")

    db.insert(
        {
            "id": str(uuid.uuid4()),
            "name": world_name,
            "filepath": world_path,
            "prompt": query,
            "total_models": placement,
            "world_name": world["World"],
        }
    )

    questionary.print(
        f"Finished! Output available at { world_path } 🦄",
        style="bold italic fg:green",
    )
