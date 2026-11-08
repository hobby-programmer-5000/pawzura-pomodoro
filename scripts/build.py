"""Build a fresh portable Windows x64 folder, validate it, then create a ZIP."""
import argparse
import hashlib
from importlib import metadata
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tomllib
import zipfile

from check_distribution import DOCS, check, digest
from build_single import build_single
from sign_windows import sign

ROOT = Path(__file__).resolve().parent.parent
NAME = "PawzuraPomodoro"


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def unify_runtime(folder):
    """Use the newest unmodified shipped MSVC runtime wherever DLL names collide."""
    import pefile
    grouped = {}
    for path in (folder / "_internal").rglob("*.dll"):
        if path.name.lower().startswith(("msvcp140", "vcruntime140", "concrt140")):
            pe = pefile.PE(str(path), fast_load=True)
            pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_RESOURCE"]])
            fixed = pe.VS_FIXEDFILEINFO[0]
            grouped.setdefault(path.name.lower(), []).append(((fixed.FileVersionMS, fixed.FileVersionLS), path))
            pe.close()
    for name, candidates in grouped.items():
        content = max(candidates, key=lambda item: item[0])[1].read_bytes()
        for path in {folder / "_internal" / name, *(p for _, p in candidates)}:
            path.write_bytes(content)


def main(dist_dir, *, single_exe=False, tool=None, thumbprint=None, signing_required=False, modified_runtime=False):
    if sys.platform != "win32" or platform.machine().lower() not in {"amd64", "x86_64"}:
        raise SystemExit("Use standard Windows x64 CPython")
    if git("status", "--porcelain"):
        raise SystemExit("Commit the reviewed source before building")
    if signing_required and not thumbprint:
        raise SystemExit("Provide a trusted signing identity; unsigned output is not permitted in this mode")
    import PySide6
    from pomodoro import __version__
    version = tomllib.loads((ROOT / "pyproject.toml").read_text("utf-8"))["project"]["version"]
    if version != __version__:
        raise SystemExit("Package and runtime versions differ")
    required = {"PySide6-Essentials": "6.12.0", "shiboken6": "6.12.0",
                "PyInstaller": "6.22.3", "pyinstaller-hooks-contrib": "2026.9"}
    if any(metadata.version(name) != expected for name, expected in required.items()):
        raise SystemExit("Install requirements-build.txt with the pinned versions")
    if not (ROOT / "licenses/SOURCES.json").is_file():
        raise SystemExit("Missing reviewed upstream license inventory")
    dist_dir = dist_dir.resolve()
    if dist_dir.exists():
        raise SystemExit("Choose a new --dist-dir; previous build outputs are preserved")
    dist_dir.mkdir(parents=True)
    work = ROOT / "build" / dist_dir.name
    work.mkdir(parents=True, exist_ok=False)
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QGuiApplication, QPainter, QPixmap
    from pomodoro.surfaces import draw_tomato
    app = QGuiApplication([])
    pixmap = QPixmap(144, 146)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    draw_tomato(painter)
    painter.end()
    icon = work / "tomato.ico"
    if not pixmap.save(str(icon), "ICO"):
        raise RuntimeError("Cannot create the tomato icon")
    version_file = work / "version.txt"
    from packaging.version import Version
    parsed = Version(version)
    numeric = (*((parsed.release + (0, 0, 0))[:3]), parsed.pre[1] if parsed.pre else 0)
    flags = 2 if parsed.is_prerelease else 0
    version_file.write_text(f"VSVersionInfo(ffi=FixedFileInfo(filevers={numeric!r}, prodvers={numeric!r}, mask=0x3f, flags={flags}, OS=0x40004, fileType=1, subtype=0, date=(0,0)), kids=[StringFileInfo([StringTable('040904B0',[StringStruct('ProductName','Pawzura Pomodoro'),StringStruct('FileDescription','Visual Pomodoro companion'),StringStruct('FileVersion',{version!r}),StringStruct('ProductVersion',{version!r}),StringStruct('OriginalFilename','PawzuraPomodoro.exe')])]),VarFileInfo([VarStruct('Translation',[1033,1200])])])", encoding="utf-8")
    manifest_file = work / "app.manifest"
    manifest_text, replaced = re.subn(r'(<assemblyIdentity version=")[^"]+',
                                     lambda match: match[1] + ".".join(map(str, numeric)),
                                     (ROOT / "scripts/windows.manifest").read_text("utf-8"), count=1)
    if replaced != 1:
        raise RuntimeError("Missing manifest identity")
    manifest_file.write_text(manifest_text, encoding="utf-8")
    environment = os.environ.copy()
    environment["PATH"] = os.pathsep.join([sys.base_prefix, str(Path(PySide6.__file__).parent),
                                           str(Path(os.environ["WINDIR"]) / "System32"), os.environ["WINDIR"]])
    args = [sys.executable, "-m", "PyInstaller", "--clean", "--onedir", "--windowed", "--noupx",
            "--name", NAME, "--icon", str(icon), "--version-file", str(version_file),
            "--manifest", str(manifest_file), "--specpath", str(work),
            "--add-data", str(ROOT / "pomodoro/art") + ";pomodoro/art",
            "--distpath", str(dist_dir), "--workpath", str(work / "pyinstaller"), str(ROOT / "run.py")]
    subprocess.run(args, cwd=ROOT, env=environment, check=True)
    output = dist_dir / NAME
    unify_runtime(output)
    signature = sign(output / f"{NAME}.exe", tool=tool, thumbprint=thumbprint, required=signing_required)
    for name in DOCS:
        shutil.copyfile(ROOT / name, output / name)
    shutil.copytree(ROOT / "licenses", output / "licenses")
    shutil.copytree(ROOT / "media", output / "media")
    installed = output / "licenses/installed"
    installed.mkdir(parents=True)
    dependencies = []
    for name in ("PySide6-Essentials", "shiboken6", "pawzura", "PyInstaller", "altgraph", "packaging",
                 "pefile", "pywin32-ctypes", "pyinstaller-hooks-contrib", "setuptools"):
        dist = metadata.distribution(name)
        dependencies.append({"name": dist.metadata["Name"], "version": dist.version,
                             "license": dist.metadata.get("License-Expression") or dist.metadata.get("License")})
        for entry in dist.files or []:
            if "licens" not in str(entry).lower() and Path(entry).name.lower() not in {"copying", "notice"}:
                continue
            source = Path(dist.locate_file(entry))
            if source.is_file() and ".." not in Path(entry).parts:
                dest = installed / name / entry
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, dest)
    python_license = Path(sys.base_prefix) / "LICENSE.txt"
    if not python_license.is_file():
        raise RuntimeError("Standard CPython LICENSE.txt required")
    shutil.copyfile(python_license, installed / "CPython-LICENSE.txt")
    tracked = git("ls-files").splitlines()
    sources = {rel: digest(ROOT / rel) for rel in tracked if rel.startswith("pomodoro/") and rel.endswith(".py")}
    sources["run.py"] = digest(ROOT / "run.py")
    info = {"version": version, "commit": git("rev-parse", "HEAD"), "python": platform.python_version(),
            "qt": "6.12.0", "mode": "onedir/dynamic Qt", "modified_upstream": modified_runtime,
            "msvc_runtime_unified": True, "dependencies": dependencies, "source_sha256": sources}
    info["signature"] = signature
    info["art_sha256"] = {p.relative_to(ROOT).as_posix(): digest(p) for p in (ROOT / "pomodoro/art").iterdir() if p.is_file()}
    (output / "BUILD-INFO.json").write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")
    validation = check(output, embedded=True)
    smoke = work / "frozen-smoke.json"
    frozen_env = os.environ.copy()
    for key in ("PYTHONPATH", "PYTHONHOME", "QT_PLUGIN_PATH", "QT_QPA_PLATFORM_PLUGIN_PATH", "QT_SCALE_FACTOR"):
        frozen_env.pop(key, None)
    frozen_env["PATH"] = os.pathsep.join([str(Path(os.environ["WINDIR"]) / "System32"), os.environ["WINDIR"]])
    frozen_env["QT_QPA_PLATFORM"] = "windows"
    subprocess.run([str(output / f"{NAME}.exe"), "--smoke-check", "--smoke-output", str(smoke)],
                   cwd=work, env=frozen_env, check=True, timeout=90)
    smoke_result = json.loads(smoke.read_text("utf-8"))
    if smoke_result.get("status") != "PASS" or smoke_result.get("version") != version or not smoke_result.get("frozen"):
        raise RuntimeError("Frozen smoke did not validate the expected build")
    manifest = {p.relative_to(output).as_posix(): digest(p) for p in output.rglob("*") if p.is_file()}
    (output / "FILE-MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    check(output, embedded=True)
    single_result = None
    if single_exe:
        executable, single_result = build_single(ROOT, output, work, dist_dir, environment, icon,
                                                version_file, manifest_file, tool=tool, thumbprint=thumbprint,
                                                signing_required=signing_required)
        single_smoke = work / "single-smoke.json"
        subprocess.run([str(executable), "--smoke-check", "--smoke-output", str(single_smoke)],
                       cwd=work, env=frozen_env, check=True, timeout=120)
        result = json.loads(single_smoke.read_text("utf-8"))
        if result.get("status") != "PASS" or result.get("version") != version or not result.get("frozen"):
            raise RuntimeError("Standalone EXE smoke did not validate the expected build")
        single_result["smoke"] = result
    archive = dist_dir / f"{NAME}-{version}-windows-x64.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for path in sorted(output.rglob("*")):
            if path.is_file():
                z.write(path, path.relative_to(output.parent).as_posix())
    checksum = archive.with_suffix(".zip.sha256")
    checksum.write_text(f"{digest(archive)}  {archive.name}\n", encoding="utf-8")
    (work / "validation.json").write_text(json.dumps({"distribution": validation, "smoke": smoke_result,
                                                     "archive_sha256": digest(archive), "single_exe": single_result}, indent=2) + "\n", encoding="utf-8")
    print(f"Built {archive.name}; SHA256 {digest(archive)}")


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist-dir", type=Path, required=True)
    parser.add_argument("--single-exe", action="store_true", help="Also build and validate a standalone EXE")
    parser.add_argument("--signtool", type=Path)
    parser.add_argument("--sign-thumbprint")
    parser.add_argument("--signing-required", action="store_true")
    parser.add_argument("--modified-runtime", action="store_true", help="Identify a rebuild with intentionally modified compatible runtime libraries")
    args = parser.parse_args()
    main(args.dist_dir, single_exe=args.single_exe, tool=args.signtool,
         thumbprint=args.sign_thumbprint, signing_required=args.signing_required, modified_runtime=args.modified_runtime)
