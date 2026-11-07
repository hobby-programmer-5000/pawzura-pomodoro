"""Render a bilingual app demo with isolated Qt widgets and synthetic displays."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import time


FPS = 12
SECONDS = 22
WIDTH, HEIGHT = 1280, 800

CAPTIONS = {
    "en": {
        "subtitle": "A walking companion for work and breaks",
        "note": "Demo desktop · time shortened",
        "display": "Display",
        "desktop": "Demo desktop",
        "focus": ("A little company while you focus", "50 minutes of work, then a 10-minute break."),
        "settings": ("Choose how you want to be reminded", "Edge glow · Companion bubble · Top banner · Dim screen · Cover screen"),
        "break": ("A break starts when work ends", "The reminder appears on both displays."),
        "waiting": ("A reminder that waits for you", "The screen stays covered until you respond."),
        "restart": ("Click Start work on either display", "Both screens clear. A fresh 50-minute session begins."),
    },
    "ko": {
        "subtitle": "작업과 휴식을 함께하는 작은 컴패니언",
        "note": "예제 화면 · 대기 시간 단축",
        "display": "모니터",
        "desktop": "예제 바탕 화면",
        "focus": ("집중하는 동안 토마토가 함께해요", "작업 50분, 그리고 휴식 10분."),
        "settings": ("알림을 원하는 모양으로 골라보세요", "테두리 빛 · 말풍선 · 상단 배너 · 반투명 덮개 · 전체 가림"),
        "break": ("작업이 끝나면 휴식이 시작돼요", "두 모니터에 함께 알려줘요."),
        "waiting": ("응답할 때까지 기다리는 알림", "휴식이 끝나면 화면을 가린 채로 기다려요."),
        "restart": ("어느 모니터에서든 작업 시작을 눌러요", "모든 화면이 열리고, 새로운 50분이 시작돼요."),
    },
}


def render(language, output, work, ffmpeg):
    # Configure Qt before importing it or the app. These are demo-owned displays.
    work.mkdir(parents=True, exist_ok=False)
    config = work / "screens.json"
    config.write_text(json.dumps({"screens": [
        {"name": "A", "x": 0, "y": 0, "width": 800, "height": 480, "dpr": 1.0},
        {"name": "B", "x": 800, "y": 0, "width": 800, "height": 480, "dpr": 1.0},
    ]}), encoding="utf-8")
    config_option = os.path.relpath(config).replace(os.sep, "/")
    os.environ["QT_QPA_PLATFORM"] = "offscreen:configfile=" + config_option

    from PySide6.QtCore import QPoint, QPointF, QRectF, QSettings, Qt
    from PySide6.QtGui import QColor, QContextMenuEvent, QFont, QFontDatabase, QImage, QLinearGradient, QPainter, QPainterPath, QPen
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication
    from pomodoro.app import Companion

    class Clock:
        now = 0.0

        def __call__(self):
            return self.now

    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)
    fonts = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
    for name in ("segoeui.ttf", "segoeuib.ttf", "malgun.ttf", "malgunbd.ttf"):
        path = fonts / name
        if path.exists():
            QFontDatabase.addApplicationFont(str(path))
    family = "Malgun Gothic" if language == "ko" else "Segoe UI"
    if family not in QFontDatabase.families():
        raise RuntimeError(f"The demo needs the installed Windows font {family}.")
    app.setFont(QFont(family, 9))
    clock = Clock()
    owner = Companion(app, QSettings(str(work / "demo.ini"), QSettings.Format.IniFormat), clock, show_tray=False)
    owner.set_language(language)
    owner.poll.stop()
    owner.pet.timer.stop()
    owner.pet.next_idle = float("inf")
    screens = sorted(app.screens(), key=lambda screen: screen.geometry().x())
    assert len(screens) == 2 and screens[0].geometry().getRect() == (0, 0, 800, 480)
    text = CAPTIONS[language]
    frames = work / "frames"
    frames.mkdir()
    targets = (QRectF(36, 136, 800, 480), QRectF(872, 220, 368, 221))
    pointer = {"point": QPointF(440, 280), "clicked": -100}
    cue_generation, cue_start = None, 0
    pointer_before_start = None

    def click(widget, frame, local=None):
        point = local or widget.rect().center()
        pointer["point"] = QPointF(widget.mapToGlobal(point))
        pointer["clicked"] = frame
        QTest.mouseClick(widget, Qt.MouseButton.LeftButton, pos=point)
        app.processEvents()

    def choose_style(style, frame):
        combo = owner.options.effect_options.style
        view = combo.view()
        index = combo.model().index(combo.findData(style), 0)
        view.setCurrentIndex(index)
        QTest.mouseMove(view.viewport(), view.visualRect(index).center())
        click(view.viewport(), frame, view.visualRect(index).center())
        assert owner.cue_settings["waiting"].style == style

    def caption(frame):
        if frame < 36:
            return text["focus"]
        if frame < 114:
            return text["settings"]
        if frame < 156:
            return text["break"]
        if frame < 216:
            return text["waiting"]
        return text["restart"]

    def draw_cursor(painter, frame):
        for screen, target in zip(screens, targets):
            if not QRectF(screen.geometry()).contains(pointer["point"]):
                continue
            point = pointer["point"] - QPointF(screen.geometry().topLeft())
            scale = target.width() / screen.geometry().width()
            painter.save()
            painter.translate(target.topLeft() + point * scale)
            if frame - pointer["clicked"] < 5:
                painter.setPen(QPen(QColor("#e8a24a"), 3))
                painter.setBrush(QColor(247, 192, 111, 65))
                painter.drawEllipse(QPointF(0, 0), 15, 15)
            cursor = QPainterPath(QPointF(0, 0))
            cursor.lineTo(0, 19)
            cursor.lineTo(5, 14)
            cursor.lineTo(10, 23)
            cursor.lineTo(14, 21)
            cursor.lineTo(9, 12)
            cursor.lineTo(17, 12)
            cursor.closeSubpath()
            painter.setPen(QPen(QColor("#f6f8fb"), 1.5))
            painter.setBrush(QColor("#273444"))
            painter.drawPath(cursor)
            painter.restore()

    def desktop(screen):
        image = QImage(800, 480, QImage.Format.Format_ARGB32_Premultiplied)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        gradient = QLinearGradient(0, 0, 800, 480)
        gradient.setColorAt(0, QColor("#edf2ec"))
        gradient.setColorAt(1, QColor("#e0e9ef"))
        painter.fillRect(image.rect(), gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#dce8df"))
        painter.drawEllipse(QRectF(520, -130, 470, 470))
        painter.setBrush(QColor("#e9eee8"))
        painter.drawEllipse(QRectF(-180, 225, 480, 480))
        painter.setPen(QColor("#5c6e70"))
        painter.setFont(QFont(family, 9))
        painter.drawText(QPointF(18, 458), text["desktop"])

        def draw_widget(widget):
            point = widget.pos() - screen.geometry().topLeft()
            painter.drawImage(point, widget.grab().toImage())

        if owner.pet.isVisible():
            draw_widget(owner.pet)
        if owner.options and owner.options.isVisible():
            draw_widget(owner.options)
            popup = owner.options.effect_options.style.view().window()
            if popup.isVisible():
                draw_widget(popup)
        if owner.pet.menu.isVisible():
            draw_widget(owner.pet.menu)
        cue = owner.cues.windows.get(screen)
        if cue and cue.isVisible():
            painter.drawImage(0, 0, cue.grab().toImage())
        painter.end()
        return image

    try:
        for frame in range(FPS * SECONDS):
            clock.now += 1 / FPS
            owner.pet.last_tick = time.monotonic() - 1 / FPS
            owner.pet.tick()
            owner.tick()
            if frame == 18:
                click(owner.pet.badge, frame)
                assert owner.timer.phase == "work"
            elif frame == 36:
                position = owner.pet.rect().center()
                pointer["point"] = QPointF(owner.pet.mapToGlobal(position))
                pointer["clicked"] = frame
                event = QContextMenuEvent(QContextMenuEvent.Reason.Mouse, position, owner.pet.mapToGlobal(position))
                app.sendEvent(owner.pet, event)
                assert owner.pet.menu.isVisible()
            elif frame == 42:
                action = owner.actions["effects_options"]
                owner.pet.menu.setActiveAction(action)
                click(owner.pet.menu, frame, owner.pet.menu.actionGeometry(action).center())
                assert owner.options.isVisible()
                owner.options.move(185, 30)
            elif frame in (48, 76, 99):
                click(owner.options.effect_options.style, frame)
            elif frame in (54, 80, 103):
                choose_style({54: "bubble", 80: "banner", 103: "cover"}[frame], frame)
            elif frame in (58, 83):
                click(owner.options.effect_options.preview, frame)
                assert owner.cues.preview
            elif frame in (72, 96):
                click(owner.cues.windows[screens[0]].buttons["dismiss"], frame)
                assert owner.cues.phase is None and owner.timer.phase == "work"
            elif frame == 106:
                click(owner.options.close_button, frame)
                assert owner.cue_settings["waiting"].style == "cover"
            elif frame == 114:
                clock.now = owner.timer.deadline
                owner.tick()
                assert owner.timer.phase == "break"
            elif frame == 156:
                clock.now = owner.timer.deadline
                owner.tick()
                assert owner.timer.phase == "waiting" and owner.timer.deadline is None
            elif frame == 216:
                click(owner.cues.windows[screens[1]].buttons["start"], frame)
                assert owner.timer.phase == "work" and owner.timer.seconds == 3000
                assert owner.cues.phase == "work" and owner.cues.effect.style == "edge"
            if 156 <= frame < 216:
                assert owner.timer.phase == "waiting" and owner.timer.deadline is None
            if frame == 198:
                pointer_before_start = QPointF(pointer["point"])
            if 198 <= frame < 216:
                button = owner.cues.windows[screens[1]].buttons["start"]
                target = QPointF(button.mapToGlobal(button.rect().center()))
                progress = (frame - 198) / 18
                eased = progress * progress * (3 - 2 * progress)
                pointer["point"] = pointer_before_start + (target - pointer_before_start) * eased
            if owner.cues.phase:
                if cue_generation != owner.cues.generation:
                    cue_generation, cue_start = owner.cues.generation, frame
                    owner.cues.animation.pause()
                elapsed = round((frame - cue_start) * 1000 / FPS)
                owner.cues.animation.setCurrentTime(min(elapsed, owner.cues.animation.duration()))
            app.processEvents()

            image = QImage(WIDTH, HEIGHT, QImage.Format.Format_RGB32)
            image.fill(QColor("#f6f5f0"))
            painter = QPainter(image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(QColor("#263a3f"))
            font = QFont(family, 26)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(QPointF(36, 54), "Pawzura Pomodoro")
            painter.setFont(QFont(family, 12))
            painter.setPen(QColor("#566c70"))
            painter.drawText(QPointF(38, 86), text["subtitle"])
            painter.drawText(QRectF(870, 34, 370, 48), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, text["note"])
            for index, (screen, target) in enumerate(zip(screens, targets)):
                painter.setPen(QColor("#566c70"))
                painter.setFont(QFont(family, 10))
                painter.drawText(target.topLeft() - QPointF(0, 12), f"{text['display']} {index + 1}")
                painter.drawImage(target, desktop(screen))
                painter.setPen(QPen(QColor("#a9b7b5"), 1))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRect(target)
            draw_cursor(painter, frame)
            title, detail = caption(frame)
            font = QFont(family, 22)
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(QColor("#263a3f"))
            painter.drawText(QPointF(36, 686), title)
            painter.setFont(QFont(family, 12))
            painter.setPen(QColor("#566c70"))
            painter.drawText(QPointF(38, 724), detail)
            painter.end()
            assert image.save(str(frames / f"frame-{frame:04}.png"))
        assert owner.timer.phase == "work" and owner.cues.phase is None
    finally:
        if owner.options:
            owner.options.close()
        owner.shutdown()
        app.aboutToQuit.disconnect(owner.shutdown)
        app.processEvents()

    prefix = output / f"pomodoro-demo-{language}"
    source = str(frames / "frame-%04d.png")
    commands = [
        [ffmpeg, "-hide_banner", "-loglevel", "warning", "-framerate", str(FPS), "-i", source,
         "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-pix_fmt", "yuv420p",
         "-movflags", "+faststart", str(prefix.with_suffix(".mp4"))],
        [ffmpeg, "-hide_banner", "-loglevel", "warning", "-framerate", str(FPS), "-i", source,
         "-filter_complex", "[0:v]split[a][b];[a]palettegen=max_colors=128:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle",
         "-loop", "0", str(prefix.with_suffix(".gif"))],
    ]
    for index, command in enumerate(commands):
        with (work / f"encode-{index}.log").open("w", encoding="utf-8") as log:
            subprocess.run(command, check=True, stdout=log, stderr=log)
    print(json.dumps({"language": language, "frames": FPS * SECONDS, "seconds": SECONDS,
                      "outputs": [prefix.with_suffix(suffix).name for suffix in (".gif", ".mp4")]}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--language", choices=("en", "ko"), required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    args = parser.parse_args()
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        parser.error("Install FFmpeg and add it to PATH to encode the demo.")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for suffix in (".gif", ".mp4"):
        if (args.output_dir / f"pomodoro-demo-{args.language}{suffix}").exists():
            parser.error("Choose a fresh output folder to preserve earlier demo assets.")
    render(args.language, args.output_dir.resolve(), args.work_dir.resolve(), ffmpeg)


if __name__ == "__main__":
    main()
