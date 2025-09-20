def get_decoding(profile: dict, seed: int):
    d = dict(profile)
    d["seed"] = seed
    return d