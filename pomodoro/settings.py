"""Keep normal desktop settings separate from source development profiles."""
from pathlib import Path
import sys

from PySide6.QtCore import QSettings


def create_settings(settings_file=None, *, frozen=None):
    if settings_file is not None:
        store = QSettings(str(Path(settings_file).resolve()), QSettings.Format.IniFormat)
    else:
        if frozen is None:
            frozen = bool(getattr(sys, "frozen", False))
        profile = "Desktop" if frozen else "Development"
        # The legacy Pawzura/Pomodoro profile was also used by manual tests.
        # Do not guess whether its valid 1-minute duration was intentional.
        store = QSettings(QSettings.Format.IniFormat, QSettings.Scope.UserScope,
                          "PawzuraPomodoro", profile)
    store.setFallbacksEnabled(False)
    return store
