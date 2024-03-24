import os

import objaverse
import trimesh
from aspose.threed import Scene
from aspose.threed.formats import ObjSaveOptions

print(objaverse.__version__)
uids = objaverse.load_uids()
print(len(uids))

lvis_annotations = objaverse.load_lvis_annotations()
reversed_dict = {}

for key, value_list in lvis_annotations.items():
    for item in value_list:
        reversed_dict[item] = key
# print(reversed_dict)
uids = lvis_annotations["wine_bottle"][:5]
for ann in objaverse.load_annotations(uids).values():
    # print(ann)
    # print('\n\n')
    # print(ann["description"])
    print(f"Name: {ann['name']}, desc: {ann['description']}")

objects = objaverse.load_objects(uids=uids)
obj_locs = list(objects.values())

print(obj_locs)


mesh = trimesh.load(list(objects.values())[4])
# trimesh.exchange.obj.export_obj(mesh)
obj, data = trimesh.exchange.export.export_obj(
    mesh, include_texture=True, return_texture=True
)
obj_path = "test_m.obj"
with open(obj_path, "w") as f:
    f.write(obj)
# save the MTL and images
for k, v in data.items():
    with open(os.path.join("./", k), "wb") as f:
        f.write(v)
# reload the mesh from the export
# rec = trimesh.load(obj_path)

# scene = Scene.from_file(
#     "/home/Alexander.Karavaev/.objaverse/hf-objaverse-v1/glbs/000-023/bear.glb"
# )

# # Specify OBJ save options
# obj_save_options = ObjSaveOptions()
# # Import materials from external material library file
# obj_save_options.enable_materials = True

# # Save it as an OBJ
# scene.save("test.obj", obj_save_options)
