"""Validate the selected portable files, hashes, embedded source and version."""
import argparse
import hashlib
import json
import marshal
from pathlib import Path
import types

ROOT = Path(__file__).resolve().parent.parent
DOCS = ("LICENSE", "README.md", "README.ko.md", "BUILD.md", "BUILD.ko.md",
        "RESULTS.md", "RESULTS.ko.md", "TESTING.md", "TESTING.ko.md",
        "INSPIRATION.md", "INSPIRATION.ko.md", "CONTRIBUTORS.md", "CONTRIBUTORS.ko.md",
        "THIRD-PARTY-NOTICES.md", "THIRD-PARTY-NOTICES.ko.md",
        "CHARACTER-POLICY.md", "CHARACTER-POLICY.ko.md", "ASSET-LICENSING.md", "ASSET-LICENSING.ko.md")

ART = "pomodoro/art/sprout-tomato-v1.json"


def check_art(info, read):
    expected = info.get("art_sha256", {})
    if ART not in expected:
        raise ValueError("Missing character inventory")
    for name, hashed in expected.items():
        if digest(ROOT / name) != hashed or hashlib.sha256(read(name)).hexdigest() != hashed:
            raise ValueError(f"Character payload mismatch: {name}")
    if json.loads(read(ART))["license"] != "MIT":
        raise ValueError("Wrong character license")
    for name in ("CHARACTER-POLICY.md", "ASSET-LICENSING.md", "LICENSE"):
        if hashlib.sha256(read(name)).hexdigest() != digest(ROOT / name):
            raise ValueError(f"Character notice mismatch: {name}")


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def normalized(code):
    return code.replace(co_filename="<source>", co_consts=tuple(
        normalized(value) if isinstance(value, types.CodeType) else value for value in code.co_consts))


def check_code(executable, info):
    from PyInstaller.archive.readers import CArchiveReader
    archive = CArchiveReader(str(executable))
    pyz = archive.open_embedded_archive("PYZ.pyz")
    for rel, expected_hash in info["source_sha256"].items():
        if digest(ROOT / rel) != expected_hash:
            raise ValueError(f"Build source changed: {rel}")
        if not rel.startswith("pomodoro/") or not rel.endswith(".py"):
            continue
        if rel == "pomodoro/__main__.py" or rel.startswith("pomodoro/tools/"):
            continue
        parts = Path(rel).with_suffix("").parts
        module = ".".join(parts[:-1] if parts[-1] == "__init__" else parts)
        actual = pyz.extract(module)
        expected = compile((ROOT / rel).read_bytes(), rel, "exec", optimize=0)
        if normalized(actual) != normalized(expected):
            raise ValueError(f"Embedded source mismatch: {module}")
    main = marshal.loads(archive.extract("run"))
    if normalized(main) != normalized(compile((ROOT / "run.py").read_bytes(), "run.py", "exec")):
        raise ValueError("Embedded entry point mismatch")
    return archive


def check_single(executable):
    from PyInstaller.archive.readers import CArchiveReader
    archive = CArchiveReader(str(executable))
    info = json.loads(archive.extract("BUILD-INFO.json"))
    if info["mode"] != "onefile/dynamic Qt, temporary extraction":
        raise ValueError("Wrong standalone build mode")
    manifest = json.loads(archive.extract("PAYLOAD-MANIFEST.json"))
    names = {name.replace("\\", "/"): name for name in archive.toc}
    if len(names) != len(archive.toc):
        raise ValueError("Duplicate normalized archive paths")
    for name in names:
        if Path(name).suffix.lower() in {".ini", ".lock", ".log"}:
            raise ValueError(f"Private settings in archive: {name}")
    for name, expected in manifest.items():
        path = Path(name)
        if path.is_absolute() or ".." in path.parts or ":" in name or path.suffix.lower() in {".ini", ".lock", ".log"}:
            raise ValueError(f"Unsafe/private single-file payload: {name}")
        if name not in names or hashlib.sha256(archive.extract(names[name])).hexdigest() != expected:
            raise ValueError(f"Single-file payload mismatch: {name}")
    for name in ("THIRD-PARTY-NOTICES.md", "THIRD-PARTY-NOTICES.ko.md", "licenses/SOURCES.json", "licenses/installed/CPython-LICENSE.txt"):
        if name not in manifest:
            raise ValueError(f"Missing embedded notice: {name}")
    check_code(executable, info)
    check_art(info, lambda name: archive.extract(names[name]))
    return {"status": "PASS", "version": info["version"], "commit": info["commit"],
            "payload_files": len(manifest), "embedded_source_checked": True}


def check(folder, *, embedded=False):
    folder = Path(folder).resolve()
    info = json.loads((folder / "BUILD-INFO.json").read_text("utf-8"))
    allowed = set(DOCS) | {"PawzuraPomodoro.exe", "_internal", "licenses", "media",
                           "BUILD-INFO.json", "FILE-MANIFEST.json"}
    extra = {p.name for p in folder.iterdir()} - allowed
    if extra:
        raise ValueError(f"Unselected distribution entries: {sorted(extra)}")
    for name in (*DOCS, "PawzuraPomodoro.exe", "licenses/SOURCES.json",
                 "licenses/installed/CPython-LICENSE.txt"):
        if not (folder / name).is_file():
            raise ValueError(f"Missing distribution file: {name}")
    paths = [p for p in folder.rglob("*") if p.is_file()]
    for p in paths:
        rel = p.relative_to(folder)
        if p.is_symlink() or any(part.startswith((".venv", ".cache")) or part in
                                 {".git", ".codex", ".agents", "__pycache__"} for part in rel.parts):
            raise ValueError(f"Local artifact: {rel}")
        if p.suffix.lower() in {".ini", ".log", ".lock", ".pdf", ".env"} or p.name.lower().startswith("agents"):
            raise ValueError(f"Private/settings/instruction artifact: {rel}")
        if p.suffix.lower() == ".json" and p.parent == folder and p.name not in {"BUILD-INFO.json", "FILE-MANIFEST.json"}:
            raise ValueError(f"Unselected JSON/profile: {rel}")
    for name in ("Qt6Core.dll", "Qt6Gui.dll", "Qt6Widgets.dll", "qwindows.dll"):
        if not list((folder / "_internal").rglob(name)):
            raise ValueError(f"Missing runtime: {name}")
    supported_qt = {"Qt6Core.dll", "Qt6Gui.dll", "Qt6Widgets.dll", "Qt6Network.dll",
                    "Qt6OpenGL.dll", "Qt6OpenGLWidgets.dll", "Qt6Svg.dll", "Qt6SvgWidgets.dll",
                    "Qt6DBus.dll", "Qt6PrintSupport.dll", "Qt6Xml.dll", "Qt6Test.dll"}
    unexpected_qt = {p.name for p in (folder / "_internal").rglob("Qt6*.dll")} - supported_qt
    if unexpected_qt:
        raise ValueError(f"Qt modules need additional source/license review: {sorted(unexpected_qt)}")
    if info["mode"] != "onedir/dynamic Qt" or info["qt"] != "6.12.0":
        raise ValueError("Unexpected Qt build")
    for rel, expected in info["source_sha256"].items():
        if digest(ROOT / rel) != expected:
            raise ValueError(f"Build source changed: {rel}")
    manifest_path = folder / "FILE-MANIFEST.json"
    if manifest_path.exists():
        expected = json.loads(manifest_path.read_text("utf-8"))
        actual = {p.relative_to(folder).as_posix(): digest(p) for p in paths if p != manifest_path}
        if actual != expected:
            raise ValueError("Distribution file manifest mismatch")
    if embedded:
        check_code(folder / "PawzuraPomodoro.exe", info)
    check_art(info, lambda name: ((folder / "_internal" / name) if name.startswith("pomodoro/") else (folder / name)).read_bytes())
    return {"status": "PASS", "files": len(paths), "version": info["version"],
            "commit": info["commit"], "embedded_source_checked": embedded}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    parser.add_argument("--embedded", action="store_true")
    parser.add_argument("--single-exe", action="store_true")
    args = parser.parse_args()
    print(json.dumps(check_single(args.folder) if args.single_exe else check(args.folder, embedded=args.embedded), indent=2))
