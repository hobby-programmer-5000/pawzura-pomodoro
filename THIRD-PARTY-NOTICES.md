[English](THIRD-PARTY-NOTICES.md) · [한국어](THIRD-PARTY-NOTICES.ko.md)

# Component licenses

Original app code, tomato artwork and demo composition use the repository's MIT license. [MIT](LICENSE).

| Component | Version | License and source |
| --- | --- | --- |
| Pawzura | 23bd3b90435d6e5ab6c0dd510d8dc5b8897489a6 | MIT. [Original license](https://github.com/hobby-programmer-5000/pawzura/blob/23bd3b90435d6e5ab6c0dd510d8dc5b8897489a6/LICENSE). |
| PySide6 Essentials | 6.12.0 | LGPL-3.0-only, selected from upstream alternatives. [Package](https://pypi.org/project/PySide6-Essentials/6.12.0/). |
| Shiboken6 | 6.12.0 | LGPL-3.0-only, selected from upstream alternatives. [Package](https://pypi.org/project/shiboken6/6.12.0/). |
| Qt Base | 6.12.0 | Applicable LGPL-3.0 terms and incorporated notices. [Qt licensing](https://doc.qt.io/qt-6/licensing.html). |
| CPython | Source: user-installed 3.12+; this portable alpha: 3.14.7 | Python Software Foundation terms and incorporated notices. [License](https://docs.python.org/3.14/license.html). |
| PyInstaller | 6.22.3 | GPL-2.0-or-later with bootloader distribution exception; some files Apache-2.0. Build tool, not a change to the app's MIT license. [Exception](https://pyinstaller.org/en/stable/license.html). |
| PyInstaller hooks | 2026.9 | Apache-2.0/GPL terms and applicable exceptions as identified in installed package notices. Build tool. [Upstream](https://github.com/pyinstaller/pyinstaller-hooks-contrib). |
| FFmpeg | 9.0.2 used for demos | Installed authoring build reports GPL-3.0-or-later. [License](https://ffmpeg.org/legal.html). |
| Windows fonts | Segoe UI / Malgun Gothic | Rasterized screen/video output. [Microsoft guidance](https://learn.microsoft.com/en-us/typography/fonts/font-faq). |

Qt/PySide bindings are dynamically loaded. Retain package notices and compatible-library replacement/relinking rights in a binary distribution. Review exact binaries and incorporated components when preparing a frozen release. [Qt LGPL obligations](https://www.qt.io/development/open-source-lgpl-obligations).

The portable ZIP includes reviewed upstream license/attribution texts and installed package notices in `licenses/`, plus CPython's license. [Source inventory](licenses/SOURCES.json) records upstream URLs and hashes of the notice files. `BUILD-INFO.json` in the ZIP identifies exact included versions and source hashes; `FILE-MANIFEST.json` identifies shipped files. Build-only dependencies may have notices included without their code being part of the executable. MSVC runtime files supplied with CPython/Qt wheels remain unmodified; when duplicate DLL names differ, the newest shipped version is used consistently.

The app and Pawzura source remain MIT. No model weights, FFmpeg executable, Windows font files or unrelated Pawzura profiles/assets are distributed. FFmpeg/fonts were used only to author the existing raster/video demo. Qt modules selected by the build are checked against the recorded runtime and retained notices; this record is not a blanket legal clearance for other modules or future versions. See [build and library replacement](BUILD.md) for corresponding source archives and LGPL rights.

Design influences are recorded in [References and inspiration](INSPIRATION.md).

The separate standalone EXE embeds the same dynamic runtime and notices and extracts them temporarily. Its LGPL compliance route supplies corresponding application code/build scripts and exact library source archives for recombination, as detailed in [BUILD](BUILD.md); the onedir ZIP continues to offer direct compatible-DLL replacement. **Options > Licenses** exposes notices and the exact build source in both formats. Original code/artwork remain MIT.
