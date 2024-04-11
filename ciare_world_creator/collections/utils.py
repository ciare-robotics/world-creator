import os

import chromadb
import pandas as pd
import questionary
import tqdm
from chromadb.config import Settings
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

from ciare_world_creator.model_databases.base import BaseLoader
from ciare_world_creator.utils.cache import Cache


def fill_index(collection, loader: BaseLoader):
    questionary.print(
        f"Generating indicies for chromadb. This might take a while, but it's done only once",
        style="bold italic fg:green",
    )
    models, _ = loader.get_models()
    df_models = pd.DataFrame(models)
    df_models = df_models.drop_duplicates(subset="name")
    df_models["tags"] = df_models["tags"].apply(
        lambda x: ", ".join(x) if isinstance(x, list) else ""
    )
    df_models["categories"] = df_models["categories"].apply(
        lambda x: ", ".join(x) if isinstance(x, list) else ""
    )

    df_models = df_models.drop_duplicates(subset="name")

    batch_size = 100

    for i in tqdm.tqdm(range(0, len(df_models), batch_size)):
        batch_df = df_models[i : i + batch_size]
        tags = batch_df["tags"].tolist()
        categories = batch_df["categories"].tolist()

        metadata = [
            {"tags": tag, "categories": category}
            for tag, category in zip(tags, categories)
        ]
        collection.upsert(
            ids=[str(idx) for idx in batch_df.index.to_list()],
            documents=(batch_df["name"]).to_list(),
            metadatas=metadata,
        )


def get_or_create_collection(name: str, loader: BaseLoader):
    # We initialize an embedding function, and provide it to the collection.
    embedding_function = OpenAIEmbeddingFunction(api_key=os.getenv("OPENAI_API_KEY"))

    cache = Cache()
    client = chromadb.Client(
        Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=os.path.join(cache.cache_path, "chromadb"),
        )
    )

    # client.delete_collection("models")
    model_collection = client.get_or_create_collection(
        name=name,
        embedding_function=embedding_function,
        metadata={"hnsw:space": "cosine"},
    )

    if model_collection.count() == 0:
        questionary.print(
            f"Indicies for models are not created yet. Filling them",
            style="bold italic fg:red",
        )
        fill_index(model_collection, loader)

    return model_collection
