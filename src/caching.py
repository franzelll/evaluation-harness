import os, json, hashlib


def make_key(model_id: str, decoding: dict, prompt: str, ex_id: str) -> str:
    payload = json.dumps(
        {"m": model_id, "d": decoding, "p": prompt, "id": ex_id}, sort_keys=True
    )
    return hashlib.sha1(payload.encode()).hexdigest()


def get(cache_dir: str, key: str):
    path = os.path.join(cache_dir, f"{key}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def put(cache_dir: str, key: str, obj: dict):
    os.makedirs(cache_dir, exist_ok=True)
    path = os.path.join(cache_dir, f"{key}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
