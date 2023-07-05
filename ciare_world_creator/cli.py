import asyncio
import os
import sys

import click
import langchain
import questionary

from ciare_world_creator.utils.cache import Cache
from ciare_world_creator.utils.style import STYLE

CONTEXT_SETTINGS = dict(auto_envvar_prefix="COMPLEX")


class WorldCreator(click.MultiCommand):
    def list_commands(self, ctx):
        rv = ["list", "create", "fix", "purge"]
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            mod = __import__(
                f"ciare_world_creator.commands.{name}", None, None, ["cli"]
            )
        except ImportError as e:
            print(e)
            return

        return mod.cli


@click.command(cls=WorldCreator, context_settings=CONTEXT_SETTINGS)
def cli():
    """World creator by Ciare"""
    cache = Cache()
    if not cache.check_api_key():
        questionary.print(
            f"OpenAI api key not found at {cache.cache_path}/openai_api_key. Generate it at https://platform.openai.com/account/api-keys at copy to file or paste here",
            style="bold italic fg:red",
        )
        api_key = questionary.password(
            "Enter your api_key here. It will be saved in the file on your pc for future usage.",
            style=STYLE,
        ).ask()
        if not api_key:
            sys.exit(os.EX_OK)

        with open(f"{cache.cache_path}/openai_api_key", "w+") as f:
            f.write(api_key)
    else:
        with open(f"{cache.cache_path}/openai_api_key", "r") as f:
            api_key = f.read()

    os.environ["OPENAI_API_KEY"] = api_key

    if cache.models_and_worlds_initialized():
        questionary.print(
            "Model database is missing at /var/tmp/ciare. Downloading it, but it may take some time...",
            style="bold italic fg:red",
        )
        cache.init_models_and_worlds()
