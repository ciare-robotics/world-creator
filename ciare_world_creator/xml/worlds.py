def find_model(model, models):
    for m in models:
        if m["name"] == model:
            return m
    return None


def find_world(world, worlds):
    for m in worlds:
        if m["name"] == world:
            return m
    return None
