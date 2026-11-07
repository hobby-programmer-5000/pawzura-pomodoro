[English](BUILD.md) · [한국어](BUILD.ko.md)

# Portable Windows build

Choose either the Windows x64 ZIP or the separate standalone EXE. For the ZIP, extract the whole folder and open `PawzuraPomodoro.exe`; keep `_internal` with it. The standalone `PawzuraPomodoro-0.1.0a2-windows-x64.exe` needs no companion folder. Both run without Python installation. The standalone file extracts its bundled runtime into a temporary directory during execution, so its first startup can take longer. The executable is unsigned. Download only from this repository's Releases page. Windows may show a reputation prompt for an unsigned alpha; verify the published SHA256 before deciding whether to run it.

Normal packaged runs share the stable per-user `%APPDATA%/PawzuraPomodoro/Desktop.ini` profile. Source runs use `Development.ini` in that directory. The old alpha-1/source-test `%APPDATA%/Pawzura/Pomodoro.ini` is preserved and is not imported: its valid 1-minute test value must not silently become the new desktop default. Fresh desktop settings are English, work 50 minutes/rest 10 minutes, walking/effects on. Subsequent desktop preferences survive updates and are shared by ZIP and standalone EXE. The **50 / 10** button beside the break time restores those durations for the next interval without interrupting an active timer.

## Build from reviewed source

Use Windows x64 with standard CPython 3.14 (not a Conda Qt environment). In a clean checkout:

```powershell
py -3.14 -m venv .venv-standard
.\.venv-standard\Scripts\python.exe -m pip install -r requirements-build.txt
.\.venv-standard\Scripts\python.exe -m unittest discover -s tests -v
.\.venv-standard\Scripts\python.exe -m pomodoro --smoke-check --smoke-output .cache/source-smoke.json
.\.venv-standard\Scripts\python.exe scripts/build.py --dist-dir dist/0.1.0a2 --single-exe
```

Commit reviewed changes first. The builder refuses dirty source and existing output directories. Use a new output name for each attempt, retaining previous evidence. Packaging tools are pinned to PyInstaller 6.22.3 and hooks 2026.9; runtime Qt/PySide/Shiboken remains 6.12.0. `BUILD-INFO.json` records the actual Python/dependency versions, Git commit and source hashes. The process is repeatable; it does not claim byte-for-byte reproducible Windows binaries.

The build creates a tomato icon, a per-monitor-DPI-aware windowed onedir executable, component notices, a file hash manifest, a ZIP and its SHA256. Qt remains dynamically linked in both formats. The ZIP exposes replaceable libraries; the standalone EXE temporarily unpacks the same unified runtime and embeds notices, build data and a payload hash manifest. **Options > Licenses** opens the notices and matching source link inside either format. The builder compares the embedded Python code with the committed source, runs the frozen EXE in a disposable profile without a Python PATH, and checks its defaults, both languages, work/break/waiting cycle, pause/resume, five previews, button layout on every screen, explicit work confirmation, stale callbacks, options and persistence. Its timer is accelerated; this is not another real 50/10-minute test.

Build evidence is stored locally under `build/<output-name>/`, including `frozen-smoke.json` and `validation.json`. It is excluded from Git and the release. If the build or smoke fails, stop publication, inspect the specific error, correct it and build into a new directory.

## Verify a downloaded archive

```powershell
Get-FileHash .\PawzuraPomodoro-0.1.0a2-windows-x64.zip -Algorithm SHA256
```

Compare it with the release's `.sha256` file. A successful hash check establishes file identity, not publisher reputation. Maintainers can also run `python scripts/check_distribution.py <extracted-folder> --embedded` from the matching source checkout with the build dependencies installed.

To diagnose the exact EXE without touching normal preferences:

```powershell
.\PawzuraPomodoro\PawzuraPomodoro.exe --smoke-check --smoke-output "$env:TEMP\pomodoro-smoke.json"
Get-Content "$env:TEMP\pomodoro-smoke.json"
```

The report must say `PASS`, `frozen: true` and version `0.1.0a2`. Diagnostic windows appear briefly and close. The command does not test tray OS input, screen lock, sleep, RDP or hardware hot-plug. See [results and limitations](RESULTS.md) and [manual scenarios](TESTING.md). Source-session Windows 11 results do not establish frozen Windows 11 compatibility until that exact binary is tested there.

For a regular interactive run with a separate profile, use `PawzuraPomodoro.exe --settings-file <new-folder>/settings.ini`. The normal menus/tray and instance lock remain active, while Windows-startup registration is disabled for this isolated profile. Use a dedicated directory; the lock is shared by profiles in the same directory. Do not rely on overriding APPDATA/LOCALAPPDATA environment variables: Qt uses Windows known-folder APIs for its default settings location.

## Components and replacement rights

Original code stays MIT. Qt/PySide/Shiboken are used under their applicable LGPLv3 options; notices and upstream attribution texts are in `licenses/`. Unmodified corresponding source is available from [Qt Base v6.12.0](https://github.com/qt/qtbase/archive/refs/tags/v6.12.0.tar.gz), [Qt SVG v6.12.0](https://github.com/qt/qtsvg/archive/refs/tags/v6.12.0.tar.gz), and [PySide/Shiboken v6.12.0](https://github.com/pyside/pyside-setup/archive/refs/tags/v6.12.0.tar.gz). Releases also provide these source archives. The pinned Pawzura source and MIT license are linked in [notices](THIRD-PARTY-NOTICES.md).

You may inspect and replace compatible Qt/PySide/Shiboken DLLs/PYD files in `_internal`, and reverse engineer the application as needed to debug your library modifications. Keep architecture and Python/Qt ABI compatibility, retain a backup, and rerun the smoke check. No signature or launcher check prevents modified-library execution; the optional manifest checker will report changed hashes. Preserve notices and source access when redistributing. These component obligations apply separately from the app's MIT license. See [Qt's LGPL guidance](https://www.qt.io/development/open-source-lgpl-obligations) and [PyInstaller's exception](https://pyinstaller.org/en/stable/license.html).

## Start with Windows

In a normal packaged run, open **Options > General > Start with Windows**. It is off by default. Enabling it creates only the app's current-user `HKCU/Software/Microsoft/Windows/CurrentVersion/Run` value; it needs no administrator access. The command quotes the permanent external EXE path, including for the standalone build, and adds `--startup`. A second login-start instance exits quietly. An unrecognized existing value is preserved and an access failure is reported.

Keep the chosen EXE in a permanent folder before enabling startup. Turn the option off before moving/deleting it; after replacing a versioned standalone file, turn startup off and on to register the new path. Source runs and `--settings-file` test profiles disable this option. To uninstall, disable startup, quit through the tray/companion menu and remove the ZIP folder or standalone file; remove Desktop.ini separately only if you want to reset preferences.

## Single-file library recombination

The standalone file embeds the dynamic libraries, so its replacement procedure differs from the ZIP. The matching application code, build scripts and requirements are available through the release's source archive or the exact commit link in **Options > Licenses**. LGPL corresponding library sources are the Qt Base/SVG/PySide archives supplied with each release. Keep the notices and offer the same source access to recipients.

To produce a modified combined work, clone that exact source revision, create the standard build environment above, replace the relevant ABI-compatible 6.12.0 Qt/PySide/Shiboken shared libraries in the build environment with your modified versions, commit any app/build edits, and run `python scripts/build.py --dist-dir dist/custom-name --single-exe --modified-runtime`. This records the modified-runtime status and repacks the supplied libraries. Code signing is optional for your rebuild and no application check requires our signing key. If you redistribute modified libraries, include their corresponding modifications/source and notices. You may debug/reverse engineer as needed for those modifications. Original application code remains MIT; onefile distribution uses the LGPL corresponding-application-code/recombination route rather than claiming its temporary DLLs are directly user-replaceable. [LGPL section 4](licenses/upstream/qtbase/LICENSES/LGPL-3.0-only.txt).

## Optional trusted signing

This alpha is intentionally unsigned. Packaging as one EXE does not remove SmartScreen warnings, and even a valid new signature does not guarantee immediate reputation. [Microsoft's current guidance](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/smartscreen-reputation).

With an already enrolled public-trust code-signing certificate in the Windows current-user My store (including a provider-backed key), add `--signtool <Windows-SDK-SignTool.exe> --sign-thumbprint <certificate-SHA1> --signing-required` to the build command. The helper requests SHA256 Authenticode plus an RFC3161 SHA256 timestamp, runs trust verification, and fails the build on signing/verification error. Both EXEs are signed before their hashes and ZIP are finalized. No private-key file/password is read by the script; do not commit certificate files or service credentials. Without the required identity the required-signing mode refuses to build. Purchasing/enrolling an identity, Store submission and disabling OS protection are outside this build command.

Automated diagnostic windows allow desktop pointer input to pass through; the diagnostic drives widget actions directly. Real OS pointer interception and login startup are separate manual checks.
