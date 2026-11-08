"""Check local document links and exact artwork/license inventory offline."""
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent


def main():
    paths = [*ROOT.glob("*.md"), *ROOT.joinpath("media").glob("*.md")]
    for path in paths:
        text = path.read_text("utf-8")
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if "://" in target or target.startswith("#"):
                continue
            local = unquote(target.split("#", 1)[0])
            if not (path.parent / local).is_file():
                raise ValueError(f"Broken link: {path.name}: {target}")
    art = ROOT / "pomodoro/art/sprout-tomato-v1.json"
    hashed = hashlib.sha256(art.read_bytes()).hexdigest()
    for name in ("ASSET-LICENSING.md", "ASSET-LICENSING.ko.md"):
        if hashed not in (ROOT / name).read_text("utf-8"):
            raise ValueError(f"Stale artwork register: {name}")
    for item in json.loads((ROOT / "licenses/SOURCES.json").read_text("utf-8")):
        if hashlib.sha256((ROOT / "licenses" / item["path"]).read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError(f"License source hash mismatch: {item['path']}")
    media = json.loads((ROOT / "media/SHA256.json").read_text("utf-8"))
    for name, hashed in media.items():
        if hashlib.sha256((ROOT / "media" / name).read_bytes()).hexdigest() != hashed:
            raise ValueError(f"Demo hash mismatch: {name}")
    print(f"PASS: {len(paths)} documents, artwork register, license sources, {len(media)} demos")


if __name__ == "__main__":
    main()
