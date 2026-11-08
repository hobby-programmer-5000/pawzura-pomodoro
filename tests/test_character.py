from copy import deepcopy
import unittest

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPainter

from pomodoro.character import artwork, draw_tomato, validate_artwork


class CharacterTests(unittest.TestCase):
    def test_rejects_malformed_or_executable_drawing_data(self):
        bad = [None, [], {"schema": True, "layers": []}]
        for path, value in [
            (("layers",), {}), (("palette",), {"bad": "url(script)"}),
            (("gradient",), "1234"), (("layers", 0), []),
            (("layers", 0, "kind"), []), (("layers", 0, "stroke"), ["outline"]),
            (("layers", 0, "standing"), None), (("layers", 0, "standing"), [0, 0, float('inf'), 0]),
            (("layers", 6, "standing", 0), ["eval", 1, 2]),
            (("layers", 6, "seated", 0), []),
            (("layers", 3, "seated"), [0, 0, -2, 4]),
            (("layers", 13, "fill"), []),
        ]:
            item = deepcopy(artwork())
            target = item
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            bad.append(item)
        for item in bad:
            with self.subTest(item=repr(item)[:60]), self.assertRaises(ValueError):
                validate_artwork(item)

    def test_seated_render_is_stationary_and_break_eyes_differ_from_waiting(self):
        def render(phase, resting, walking=True, seated=1):
            image = QImage(144, 146, QImage.Format.Format_ARGB32_Premultiplied)
            image.fill(Qt.GlobalColor.transparent)
            painter = QPainter(image)
            draw_tomato(painter, phase=phase, walking=walking, resting=resting, seated=seated)
            painter.end()
            return image
        asleep = render(0, True)
        self.assertEqual(asleep, render(1.7, True))
        waiting = render(0, False)
        self.assertNotEqual(asleep.copy(45, 95, 55, 20), waiting.copy(45, 95, 55, 20))
        self.assertEqual(asleep.copy(0, 120, 144, 26), waiting.copy(0, 120, 144, 26))
        self.assertNotEqual(render(0, False, seated=0), render(1.7, False, seated=0))
