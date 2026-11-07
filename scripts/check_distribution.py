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
        "THIRD-PARTY-NOTICES.md", "THIRD-PARTY-NOTICES.ko.md")


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def normalized(code):
    return code.replace(co_filename="<source>", co_consts=tuple(
        normalized(value) if isinstance(value, types.CodeType) else value for value in code.co_consts))


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
        from PyInstaller.archive.readers import CArchiveReader
        archive = CArchiveReader(str(folder / "PawzuraPomodoro.exe"))
        pyz = archive.open_embedded_archive("PYZ.pyz")
        for rel in info["source_sha256"]:
            if not rel.startswith("pomodoro/") or not rel.endswith(".py"):
                continue
            # Source provenance also records the `python -m` wrapper and demo
            # authoring tools. The frozen app enters through run.py and never
            # imports these development-only files.
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
    return {"status": "PASS", "files": len(paths), "version": info["version"],
            "commit": info["commit"], "embedded_source_checked": embedded}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    parser.add_argument("--embedded", action="store_true")
    args = parser.parse_args()
    print(json.dumps(check(args.folder, embedded=args.embedded), indent=2))
