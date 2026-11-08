"""Opt-in, current-user Windows login startup; construction never writes."""
from pathlib import Path
import subprocess

VALUE = "PawzuraPomodoro"
KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


class RunKey:
    def read(self):
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, KEY) as key:
                value, kind = winreg.QueryValueEx(key, VALUE)
                return value if kind == winreg.REG_SZ and isinstance(value, str) else "<unrecognized>"
        except FileNotFoundError:
            return None

    def write(self, command):
        import winreg
        with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, KEY, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, VALUE, 0, winreg.REG_SZ, command)

    def delete(self):
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, KEY, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, VALUE)
        except FileNotFoundError:
            pass


def command_args(command):
    import ctypes
    from ctypes import wintypes
    shell = ctypes.WinDLL("shell32", use_last_error=True)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    shell.CommandLineToArgvW.argtypes = (wintypes.LPCWSTR, ctypes.POINTER(ctypes.c_int))
    shell.CommandLineToArgvW.restype = ctypes.POINTER(wintypes.LPWSTR)
    kernel.LocalFree.argtypes = (ctypes.c_void_p,)
    kernel.LocalFree.restype = ctypes.c_void_p
    count = ctypes.c_int()
    pointer = shell.CommandLineToArgvW(command, ctypes.byref(count))
    if not pointer:
        raise OSError("Cannot read startup command")
    try:
        return [pointer[index] for index in range(count.value)]
    finally:
        kernel.LocalFree(pointer)


class Startup:
    def __init__(self, executable, registry=None):
        self.executable = Path(executable).resolve()
        self.registry = registry if registry is not None else RunKey()

    @property
    def command(self):
        return subprocess.list2cmdline([str(self.executable), "--startup"])

    def owns(self, command):
        if not isinstance(command, str) or len(command) > 32767:
            return False
        if command == self.command:
            return True
        args = command_args(command)
        return (len(args) == 2 and args[1] == "--startup"
                and Path(args[0]).name.lower().startswith("pawzurapomodoro")
                and Path(args[0]).suffix.lower() == ".exe")

    def enabled(self):
        command = self.registry.read()
        return bool(command and self.owns(command))

    def set_enabled(self, enabled):
        current = self.registry.read()
        if current and not self.owns(current):
            raise ValueError("The startup entry belongs to an unrecognized command")
        if enabled:
            if not self.executable.is_file() or self.executable.suffix.lower() != ".exe":
                raise ValueError("Keep the executable in its permanent location first")
            self.registry.write(self.command)
        else:
            self.registry.delete()
