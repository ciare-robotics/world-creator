import objaverse
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


# trimesh.load(list(objects.values())[4]).show()


scene = Scene.from_file(
    "/home/Alexander.Karavaev/.objaverse/hf-objaverse-v1/glbs/000-023/bear.glb"
)

# Specify OBJ save options
obj_save_options = ObjSaveOptions()
# Import materials from external material library file
obj_save_options.enable_materials = True

# Save it as an OBJ
scene.save("test.obj", obj_save_options)
