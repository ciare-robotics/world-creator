import glob

from setuptools import find_packages, setup

setup(
    name="ciare-world-creator",
    version="0.1.0",
    author="Aleksandr Karavaev",
    author_email="alexkaravaev@alexkaravaev.xyz",
    description="World creator",
    url="https://twitter.com",
    classifiers=["Programming Language :: Python :: 3", "License :: Magazino"],
    py_modules=["completion"],
    packages=[
        "ciare_world_creator",
        "ciare_world_creator.commands",
        "ciare_world_creator.utils",
        "ciare_world_creator.llm",
        "ciare_world_creator.collections",
        "ciare_world_creator.contexts_prompts",
        "ciare_world_creator.model_databases",
        "ciare_world_creator.xml",
    ],
    include_package_data=True,
    entry_points={
        "console_scripts": ["ciare_world_creator = ciare_world_creator.cli:cli"]
    },
)
