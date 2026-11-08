[English](README.md) · [한국어](README.ko.md)

# Screen demos

English/Korean GIF and MP4 are each 36 seconds, 1280 × 800, 12 fps (432 frames). They show saved Classic/Mint apron selection, 50/10 defaults, optional startup, reminder controls, sit/sleep/wait and standing before walking. Character selection has no license explanation underneath; the separate Licenses button remains available.

Actual Qt widgets are captured on two synthetic desktops with disposable settings, an accelerated countdown and independent continuous pose clock. The enlarged companion is the same widget. Startup uses an in-memory backend and never changes this machine's Run entry. These recordings are not live desktop/hardware tests.

To regenerate, use the existing Qt-compatible environment and FFmpeg on PATH with fresh output/work directories. The encoder refuses existing files.

```powershell
.\.venv-standard\Scripts\python.exe -m pomodoro.tools.record_demo --language en --output-dir .cache/demo-output --work-dir .cache/demo-work-en
.\.venv-standard\Scripts\python.exe -m pomodoro.tools.record_demo --language ko --output-dir .cache/demo-output --work-dir .cache/demo-work-ko
```

Review all four outputs before replacing repository media. [SHA256.json](SHA256.json) identifies the exact files. All four were fully decoded and checked for 432 frames/36 seconds; encoded choices, posture and bilingual captions were visually inspected. Earlier candidates/releases are preserved.

Original demo text, composition and both character images use [MIT](../LICENSE). Credit: hobby-programmer-5000; AI-assisted procedural vector art/media with ChatGPT/Codex. [Artwork record](../ASSET-LICENSING.md) · [Component notices](../THIRD-PARTY-NOTICES.md). Earlier grants remain available; this version offers MIT for the mint-apron artwork too.

FFmpeg 9.0.2 was used only as an authoring tool; the installed build reports GPL-3.0-or-later ([FFmpeg terms](https://ffmpeg.org/legal.html)). Installed Windows Segoe UI/Malgun Gothic fonts were rasterized into frames; no font files or FFmpeg executable are distributed ([Microsoft font FAQ](https://learn.microsoft.com/en-us/typography/fonts/font-faq)). Qt/runtime terms remain separate.
