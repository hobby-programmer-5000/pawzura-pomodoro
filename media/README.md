[English](README.md) · [한국어](README.ko.md)

# Screen demos

The English and Korean GIF/MP4 demos are 30 seconds, 1280 × 800 pixels, and 12 frames per second. The alpha-2 recordings demonstrate walking, 50/10 General options, optional Windows startup, reminder settings, bubble/banner previews, a break, a persistent cover, and starting a full work interval from the second display. The final caption identifies ZIP and standalone EXE choices.

Frames are captured from the app's actual Qt widgets and composed over two synthetic desktops. Settings are temporary. The clock is shortened and a cursor indicator is added for clarity. The display arrangement illustrates the app's multi-monitor behavior. Native verification results are recorded separately in the project checkpoints.

The paired project READMEs embed the GIFs and link the MP4s. GitHub supports displaying GIF images. [GitHub image documentation](https://docs.github.com/en/repositories/working-with-files/using-files/working-with-non-code-files).

To regenerate on Windows, use the existing Qt-compatible environment and an FFmpeg installation on PATH. Run these commands from the checkout root with fresh output and work directories.

```powershell
.\.venv-standard\Scripts\python.exe -m pomodoro.tools.record_demo --language en --output-dir .cache/demo-output --work-dir .cache/demo-work-en
.\.venv-standard\Scripts\python.exe -m pomodoro.tools.record_demo --language ko --output-dir .cache/demo-output --work-dir .cache/demo-work-ko
```

Review the output before copying the four GIF/MP4 files into this directory. The script preserves existing outputs by requiring fresh paths.

These demos were encoded with FFmpeg 9.0.2. The installed authoring build reports GPL-3.0-or-later. [FFmpeg licensing information](https://ffmpeg.org/legal.html).

Original demo text, composition and tomato artwork follow the repository's [MIT license](../LICENSE). The Qt/PySide runtime follows the existing [dependency notices](../THIRD-PARTY-NOTICES.md). Locally installed Windows fonts are rendered into bitmap frames, as covered by Microsoft's graphic and video output guidance. [Microsoft font FAQ](https://learn.microsoft.com/en-us/typography/fonts/font-faq).

Windows-startup toggles in the recording use an in-memory backend, not this machine's Run registry entry. The UI and event handlers are real; actual login/reboot behavior is tested separately. Versioned filenames preserve language/version in the basename, and the encoder refuses existing files.
