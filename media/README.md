[English](README.md) · [한국어](README.ko.md)

# Screen demos

The English and Korean GIF/MP4 demos are 36 seconds, 1280 × 800 pixels, and 12 frames per second. The alpha-3 recordings demonstrate choosing Classic/Mint apron, walking, 50/10 General options, optional Windows startup, reminder settings, bubble/banner previews, stopping and sitting down with closed eyes at break start, seated waiting after dismissing the cover on the second display, and starting work with the timer badge: stand up first, then walk. The separate enlarged companion view is captured from the same actual widget, including while reminders cover the desktops. The final caption identifies ZIP and standalone EXE choices.

Frames are captured from the app's actual Qt widgets and composed over two synthetic desktops. Settings are temporary. The clock is shortened and a cursor indicator is added for clarity. The display arrangement illustrates the app's multi-monitor behavior. Native verification results are recorded separately in the project checkpoints.

The paired project READMEs embed the GIFs and link the MP4s. GitHub supports displaying GIF images. [GitHub image documentation](https://docs.github.com/en/repositories/working-with-files/using-files/working-with-non-code-files).

To regenerate on Windows, use the existing Qt-compatible environment and an FFmpeg installation on PATH. Run these commands from the checkout root with fresh output and work directories.

```powershell
.\.venv-standard\Scripts\python.exe -m pomodoro.tools.record_demo --language en --output-dir .cache/demo-output --work-dir .cache/demo-work-en
.\.venv-standard\Scripts\python.exe -m pomodoro.tools.record_demo --language ko --output-dir .cache/demo-output --work-dir .cache/demo-work-ko
```

Review the output before copying the four GIF/MP4 files into this directory. The script preserves existing outputs by requiring fresh paths.

These demos were encoded with FFmpeg 9.0.2. The installed authoring build reports GPL-3.0-or-later. [FFmpeg licensing information](https://ffmpeg.org/legal.html).

Original demo text and composition remain [MIT](../LICENSE). New character imagery in `pomodoro-demo-0.1.0a3-en.gif`, `pomodoro-demo-0.1.0a3-en.mp4`, `pomodoro-demo-0.1.0a3-ko.gif` and `pomodoro-demo-0.1.0a3-ko.mp4` reproduces the designated **Sprout Tomato — mint apron edition v1** and follows **CC BY-NC-SA 4.0** for rights the licensor can grant. Credit: hobby-programmer-5000; AI-assisted vector artwork with ChatGPT/Codex. [Asset register](../ASSET-LICENSING.md) · [Unmodified CC text](../licenses/CC-BY-NC-SA-4.0.txt) · [Separate ordinary paid-work app-use permission](../CHARACTER-POLICY.md). When sharing these complete demos, retain these notices and comply with the character terms; MIT portions and third-party material keep their respective terms. Previous alpha-1/2 media retain MIT grants. The Qt/PySide runtime follows the existing [dependency notices](../THIRD-PARTY-NOTICES.md). Locally installed Windows fonts are rendered into bitmap frames, as covered by Microsoft's graphic and video output guidance. [Microsoft font FAQ](https://learn.microsoft.com/en-us/typography/fonts/font-faq).

Windows-startup toggles in the recording use an in-memory backend, not this machine's Run registry entry. The UI and event handlers are real; actual login/reboot behavior is tested separately. Versioned filenames preserve language/version in the basename, and the encoder refuses existing files.

Exact file hashes are in [SHA256.json](SHA256.json). First version: 0.1.0a3, 2026-11-08. The continuous pose clock is independent of shortened countdown jumps; per-frame posture assertions verify stationarity through the rest/wait/rise sequence. All four encoded outputs were decoded fully and checked for 432 frames, 1280 × 800 and 36 seconds; encoded pose/caption samples were visually reviewed in both languages. Previous release assets are unchanged; earlier source media remain in Git history.

Classic-tomato imagery remains MIT; the CC designation applies to the new mint-apron character portions. Selection uses the actual General options combo box and asserts the choice is persisted.
