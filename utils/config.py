import json
import os

def carregar_config(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {"tema_escuro": True, "ultima_pasta": ""}

def salvar_config(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
