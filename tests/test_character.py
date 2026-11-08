from copy import deepcopy
import unittest

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPainter

from pomodoro.character import CHARACTERS, artwork, draw_tomato, safe_character, validate_artwork


class CharacterTests(unittest.TestCase):
    def test_unknown_character_falls_back_without_loading_external_data(self):
        for value in (None, "../custom.json", [], 42, "", "unknown"):
            self.assertEqual(safe_character(value), "sprout")
        for value in CHARACTERS:
            self.assertEqual(safe_character(value), value)

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
        def render(character, phase, resting, walking=True, seated=1):
            image = QImage(144, 146, QImage.Format.Format_ARGB32_Premultiplied)
            image.fill(Qt.GlobalColor.transparent)
            painter = QPainter(image)
            draw_tomato(painter, phase=phase, walking=walking, resting=resting, seated=seated, character=character)
            painter.end()
            return image
        for character in CHARACTERS:
            with self.subTest(character=character):
                asleep = render(character, 0, True)
                self.assertEqual(asleep, render(character, 1.7, True))
                waiting = render(character, 0, False)
                self.assertNotEqual(asleep, waiting)
                self.assertEqual(asleep.copy(0, 120, 144, 26), waiting.copy(0, 120, 144, 26))
                self.assertNotEqual(render(character, 0, False, seated=0), render(character, 1.7, False, seated=0))
        self.assertNotEqual(render("classic", 0, False), render("sprout", 0, False))
