# -*- coding: utf-8 -*-
"""Zero · Importador de Codex Pets (spritesheet atlas 8xN)."""
from __future__ import annotations
import json, os, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

# Standard Codex pet atlas layout (from codex-pets-react)
CELL_W, CELL_H = 192, 208
COLS = 8
ANIM_ROWS = {
    "idle": 0, "running-right": 1, "running-left": 2, "waving": 3,
    "jumping": 4, "failed": 5, "waiting": 6, "running": 7, "review": 8,
}
ANIM_FRAMES = {
    "idle": 6, "running-right": 8, "running-left": 8, "waving": 4,
    "jumping": 5, "failed": 8, "waiting": 6, "running": 6, "review": 6,
}
# Map Codex animation -> Zero state
MAP = {
    "idle": "idle", "waiting": "thinking", "failed": "error",
    "waving": "happy", "jumping": "dashing", "running-right": "running",
    "running-left": "running", "running": "walking", "review": "analyzing",
}


def import_pet(pet_id, owner="YaKun9", repo="codex-pets", branch="main"):
    base_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{pet_id}"
    pet_dir = ASSETS / pet_id / "sprites"
    pet_dir.mkdir(parents=True, exist_ok=True)

    # fetch pet.json
    import urllib.request as u
    pet_json_url = f"{base_url}/pet.json"
    pet_json_path = pet_dir / "pet.json"
    u.urlretrieve(pet_json_url, pet_json_path)
    pet = json.loads(pet_json_path.read_text(encoding="utf-8"))

    sprite_name = pet.get("spritesheetPath", "spritesheet.webp")
    sprite_url = f"{base_url}/{sprite_name}"
    sprite_path = pet_dir / sprite_name
    u.urlretrieve(sprite_url, sprite_path)

    # slice spritesheet
    from PIL import Image
    img = Image.open(sprite_path).convert("RGBA")
    cols = img.width // CELL_W
    rows = img.height // CELL_H

    states = {}
    for anim, row in ANIM_ROWS.items():
        if row >= rows:
            continue
        nframes = min(ANIM_FRAMES[anim], cols)
        # build horizontal strip
        strip = Image.new("RGBA", (CELL_W * nframes, CELL_H))
        for i in range(nframes):
            cell = img.crop((i * CELL_W, row * CELL_H, (i + 1) * CELL_W, (row + 1) * CELL_H))
            strip.paste(cell, (i * CELL_W, 0))
        zero_state = MAP.get(anim, anim)
        out_name = f"{zero_state}.png"
        strip.save(pet_dir / out_name)
        fps = 8
        states[zero_state] = {"file": out_name, "frames": nframes, "fps": fps, "loop": anim not in ("jumping", "waving", "review")}

    # ensure idle exists
    if "idle" not in states:
        states["idle"] = {"file": list(states.values())[0]["file"], "frames": 1, "fps": 1, "loop": True}

    manifest = {
        "name": pet.get("displayName", pet_id),
        "size": [CELL_W, CELL_H],
        "default": "idle",
        "states": states,
    }
    (pet_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    # preview
    try:
        u.urlretrieve(f"{base_url}/preview.webp", pet_dir / "preview.webp")
    except Exception:
        pass

    return pet_id, pet.get("displayName", pet_id)
