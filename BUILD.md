[English](BUILD.md) · [한국어](BUILD.ko.md)

# Portable Windows build

The alpha release is a Windows x64 ZIP with `PawzuraPomodoro.exe` and its `_internal` folder. Extract the entire ZIP into a writable folder and open the EXE. Python installation is not needed. Keep the folders together. The executable is unsigned. Download only from this repository's Releases page. Windows may show a reputation prompt for an unsigned alpha; verify the published SHA256 before deciding whether to run it.

Settings are saved per user under `%APPDATA%/Pawzura/Pomodoro.ini`. Fresh settings use English, 50 minutes of work, 10 minutes of rest, walking on and visual effects on. Exit using the companion/tray menu. To remove the app, exit and delete its extracted folder; delete the settings file separately if you also want to reset preferences.

## Build from reviewed source

Use Windows x64 with standard CPython 3.14 (not a Conda Qt environment). In a clean checkout:

```powershell
py -3.14 -m venv .venv-standard
.\.venv-standard\Scripts\python.exe -m pip install -r requirements-build.txt
.\.venv-standard\Scripts\python.exe -m unittest discover -s tests -v
.\.venv-standard\Scripts\python.exe -m pomodoro --smoke-check --smoke-output .cache/source-smoke.json
.\.venv-standard\Scripts\python.exe scripts/build.py --dist-dir dist/0.1.0a1
```

Commit reviewed changes first. The builder refuses dirty source and existing output directories. Use a new output name for each attempt, retaining previous evidence. Packaging tools are pinned to PyInstaller 6.22.3 and hooks 2026.9; runtime Qt/PySide/Shiboken remains 6.12.0. `BUILD-INFO.json` records the actual Python/dependency versions, Git commit and source hashes. The process is repeatable; it does not claim byte-for-byte reproducible Windows binaries.

The build creates a tomato icon, a per-monitor-DPI-aware windowed onedir executable, component notices, a file hash manifest, a ZIP and its SHA256. Qt remains dynamically linked; it is not packed into a single-file executable. The builder compares the embedded Python code with the committed source, runs the frozen EXE in a disposable profile without a Python PATH, and checks its defaults, both languages, work/break/waiting cycle, pause/resume, five previews, button layout on every screen, explicit work confirmation, stale callbacks, options and persistence. Its timer is accelerated; this is not another real 50/10-minute test.

Build evidence is stored locally under `build/<output-name>/`, including `frozen-smoke.json` and `validation.json`. It is excluded from Git and the release. If the build or smoke fails, stop publication, inspect the specific error, correct it and build into a new directory.

## Verify a downloaded archive

```powershell
Get-FileHash .\PawzuraPomodoro-0.1.0a1-windows-x64.zip -Algorithm SHA256
```

Compare it with the release's `.sha256` file. A successful hash check establishes file identity, not publisher reputation. Maintainers can also run `python scripts/check_distribution.py <extracted-folder> --embedded` from the matching source checkout with the build dependencies installed.

To diagnose the exact EXE without touching normal preferences:

```powershell
.\PawzuraPomodoro\PawzuraPomodoro.exe --smoke-check --smoke-output "$env:TEMP\pomodoro-smoke.json"
Get-Content "$env:TEMP\pomodoro-smoke.json"
```

The report must say `PASS`, `frozen: true` and version `0.1.0a1`. Diagnostic windows appear briefly and close. The command does not test tray OS input, screen lock, sleep, RDP or hardware hot-plug. See [results and limitations](RESULTS.md) and [manual scenarios](TESTING.md). Source-session Windows 11 results do not establish frozen Windows 11 compatibility until that exact binary is tested there.

For a regular interactive run with a separate profile, use `PawzuraPomodoro.exe --settings-file <new-folder>/settings.ini`. The normal menus/tray and instance lock remain active. Use a dedicated directory; the lock is shared by profiles in the same directory. Do not rely on overriding APPDATA/LOCALAPPDATA environment variables: Qt uses Windows known-folder APIs for its default settings location.

## Components and replacement rights

Original code stays MIT. Qt/PySide/Shiboken are used under their applicable LGPLv3 options; notices and upstream attribution texts are in `licenses/`. Unmodified corresponding source is available from [Qt Base v6.12.0](https://github.com/qt/qtbase/archive/refs/tags/v6.12.0.tar.gz), [Qt SVG v6.12.0](https://github.com/qt/qtsvg/archive/refs/tags/v6.12.0.tar.gz), and [PySide/Shiboken v6.12.0](https://github.com/pyside/pyside-setup/archive/refs/tags/v6.12.0.tar.gz). Releases also provide these source archives. The pinned Pawzura source and MIT license are linked in [notices](THIRD-PARTY-NOTICES.md).

You may inspect and replace compatible Qt/PySide/Shiboken DLLs/PYD files in `_internal`, and reverse engineer the application as needed to debug your library modifications. Keep architecture and Python/Qt ABI compatibility, retain a backup, and rerun the smoke check. No signature or launcher check prevents modified-library execution; the optional manifest checker will report changed hashes. Preserve notices and source access when redistributing. These component obligations apply separately from the app's MIT license. See [Qt's LGPL guidance](https://www.qt.io/development/open-source-lgpl-obligations) and [PyInstaller's exception](https://pyinstaller.org/en/stable/license.html).
