import os

import click
import questionary
from click import pass_context
from tabulate import tabulate
from tinydb import Query, TinyDB

from ciare_world_creator.utils.cache import Cache


@click.command(
    "list",
    short_help="Lists all merge requests created by you in magdistro and allows you to perform actions on them",
)
@pass_context
def cli(ctx):
    cache = Cache()
    db = TinyDB(os.path.join(cache.worlds_path, "world_db.json"))

    documents = db.all()
    cap_string = lambda string: (string[:35] + "...") if len(string) > 35 else string

    # Convert documents to a list of dictionaries
    doc_list = [doc for doc in documents]
    updated_doc_list = []

    for doc in doc_list:
        doc["total_models"] = len(doc["total_models"])
        modified_doc = {key: cap_string(str(value)) for key, value in doc.items()}
        updated_doc_list.append(modified_doc)

    doc_list = updated_doc_list

    # Check if any documents are present
    if len(doc_list) > 0:
        doc_list[0].keys()
        # Get the keys of the first document as table headers
        headers = list(doc_list[0].keys())

        # Format the documents as a table
        table = [[doc[key] for key in headers] for doc in doc_list]

        # Print the table
        questionary.print(
            tabulate(table, headers, tablefmt="fancy_grid"),
            style="bold italic fg:green",
        )
    else:
        questionary.print(
            "Populate the database first, it's empty! Run `ciare_world_creator create`",
            style="bold italic fg:green",
        )
