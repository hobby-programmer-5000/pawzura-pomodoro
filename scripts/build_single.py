"""Repackage the already unified portable runtime into a standalone executable."""
import json
from pathlib import Path
import subprocess
import sys

from check_distribution import DOCS, check_single, digest
from sign_windows import sign


def build_single(root, folder, work, dist_dir, environment, icon, version_file, manifest_file,
                 *, tool=None, thumbprint=None, signing_required=False):
    info = json.loads((folder / "BUILD-INFO.json").read_text("utf-8"))
    info["mode"] = "onefile/dynamic Qt, temporary extraction"
    # The executable is signed only after packing; these bytes describe policy.
    info["signature_policy"] = "required" if signing_required else "optional"
    resources = work / "single-resources"
    resources.mkdir()
    (resources / "BUILD-INFO.json").write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")
    payload = []
    for path in sorted((folder / "_internal").rglob("*")):
        if path.is_file():
            kind = "BINARY" if path.suffix.lower() in {".dll", ".pyd", ".exe"} else "DATA"
            payload.append((path.relative_to(folder / "_internal").as_posix(), str(path), kind))
    for name in DOCS:
        payload.append((name, str(folder / name), "DATA"))
    for name in ("licenses", "media"):
        for path in sorted((folder / name).rglob("*")):
            if path.is_file():
                payload.append((path.relative_to(folder).as_posix(), str(path), "DATA"))
    payload.append(("BUILD-INFO.json", str(resources / "BUILD-INFO.json"), "DATA"))
    manifest = {name: digest(Path(source)) for name, source, _ in payload}
    (resources / "PAYLOAD-MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    payload.append(("PAYLOAD-MANIFEST.json", str(resources / "PAYLOAD-MANIFEST.json"), "DATA"))
    name = f"PawzuraPomodoro-{info['version']}-windows-x64"
    spec = work / "single.spec"
    source = f'''a = Analysis([{str(root / 'run.py')!r}], pathex=[{str(root)!r}], binaries=[], datas=[], hiddenimports=[], hookspath=[], runtime_hooks=[], excludes=[], noarchive=False, optimize=0)
pyz = PYZ(a.pure)
payload = {payload!r}
exe = EXE(pyz, a.scripts, payload, [], name={name!r}, debug=False, bootloader_ignore_signals=False, strip=False, upx=False, console=False, icon={str(icon)!r}, version={str(version_file)!r}, manifest={str(manifest_file)!r})
'''
    spec.write_text(source, encoding="utf-8")
    subprocess.run([sys.executable, "-m", "PyInstaller", "--clean", "--distpath", str(dist_dir),
                    "--workpath", str(work / "single-work"), str(spec)], cwd=root, env=environment, check=True)
    executable = dist_dir / f"{name}.exe"
    signature = sign(executable, tool=tool, thumbprint=thumbprint, required=signing_required)
    validation = check_single(executable)
    executable.with_suffix(".exe.sha256").write_text(f"{digest(executable)}  {executable.name}\n", encoding="utf-8")
    return executable, {**validation, "signature": signature, "sha256": digest(executable)}
