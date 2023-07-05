import os
import shutil
import sys

import click
import questionary
from click import pass_context
from tinydb import Query, TinyDB

from ciare_world_creator.utils.cache import Cache
from ciare_world_creator.utils.style import STYLE


@click.command(
    "purge",
    short_help="Delete database and all of the worlds you've created",
)
@pass_context
def cli(ctx):
    cache = Cache()
    db = TinyDB(os.path.join(cache.worlds_path, "world_db.json"))

    yes = questionary.confirm(
        "This will delete the database and all created worlds!! Are you sure??",
        style=STYLE,
    ).ask()
    if not yes:
        sys.exit(os.EX_OK)

    db.truncate()
    shutil.rmtree(cache.worlds_path)

    questionary.print(
        f"Deleted all your beatiful worlds...",
        style="bold italic fg:green",
    )
