import objaverse

from ciare_world_creator.model_databases.base import BaseLoader


class ObjaverseLoader(BaseLoader):
    def __init__(self):
        lvis_annotations = objaverse.load_lvis_annotations()

        truncated_annotations = (
            {}
        )  # Only take 3 annotations from each of the category, we don't need more
        for key, value_list in lvis_annotations.items():
            truncated_annotations[key] = value_list[:3]

        self.uid_to_category = {}
        for key, value_list in truncated_annotations.items():
            for item in value_list:
                self.uid_to_category[item] = key

        self.annotations = objaverse.load_annotations(self.uid_to_category.keys())

    def get_models(self):
        only_description_models = []

        for uuid, category in self.uid_to_category.items():
            only_description_models.append(
                {
                    "uuid": uuid,
                    "name": self.annotations[uuid]["name"],
                    "categories": [category],
                    "tags": [tag["name"] for tag in self.annotations[uuid]["tags"]],
                }
            )

        return only_description_models, None
