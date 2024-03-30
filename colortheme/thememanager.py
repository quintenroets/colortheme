import time
from functools import cache

import cli
import dbus
import gui
from backup.backups import profile
from libs.threading import Threads

from .eventchecker import EventChecker
from .path import Path


def start_check_service():
    EventChecker(
        on_light=lambda: check_theme("light"), on_dark=lambda: check_theme("dark")
    ).start()


def restartplasma():
    ThemeManager.plasma_interface.refreshCurrentShell()
    cli.run("kwin --replace", wait=False)


def check_theme(name):
    if profile.Backup().profile_name != name:
        apply(name, ask_confirm=True)


def apply(name: str, ask_confirm=False):
    confirmed = (
        not ask_confirm
        or not any(ThemeManager.open_programs())
        or gui.ask_yn(f"Change to {name} theme?")
    )
    if confirmed:
        ThemeManager.start_apply(name)

    return confirmed


class ThemeManager:
    @classmethod
    @property
    @cache
    def plasma_interface(cls):
        bus = dbus.SessionBus()
        obj = bus.get_object("org.kde.plasmashell", "/PlasmaShell")
        return dbus.Interface(obj, dbus_interface="org.kde.PlasmaShell")

    @classmethod
    def run_kde_script(cls, script: str):
        return cls.plasma_interface.evaluateScript(script)

    @classmethod
    def open_programs(cls):
        def is_open(program: str):
            return cli.completes_successfully("xdotool search --onlyvisible", program)

        programs = ["dolphin", "kate"]
        return [program for program in programs if is_open(program)]

    @classmethod
    def start_apply(cls, theme):
        custom_apply_mapping = {
            # "chromium": apply_chromium,
            # "pycharm": apply_pycharm,
        }
        custom_apply = set({})
        open_programs = cls.open_programs()

        for program, function in custom_apply_mapping.items():
            if program in open_programs:
                open_programs.remove(program)
                custom_apply.add(function)

        profile.Backup().apply_profile(theme)
        cls.apply_desktop_image(theme)
        cls.apply_start_icon(theme)
        restartplasma()
        Threads(restart, args=(open_programs,)).start().join()

        for custom in custom_apply:
            time.sleep(2)
            custom(theme)

    @classmethod
    def apply_desktop_image(cls, theme: str):
        image_path = cls.get_desktop_image()
        new_desktop_image_name = "background" if theme == "light" else "background_dark"
        new_path = image_path.with_stem(new_desktop_image_name)
        cls.set_desktop_image(new_path)

    @classmethod
    def get_desktop_image(cls):
        script_path = Path.script_templates / "getWallpaper.js"
        image_path_str = cls.run_kde_script(script_path.text)
        return Path.from_uri(image_path_str)

    @classmethod
    def set_desktop_image(cls, path):
        script_path = Path.script_templates / "setWallpaper.js"
        script = script_path.text.replace("IMAGE_PATH", path.as_uri())
        cls.run_kde_script(script)

    @classmethod
    def apply_start_icon(cls, theme: str):
        icon_path = cls.get_start_icon()
        new_icon_name = "start_menu" if theme == "light" else "start_menu_dark_theme"
        new_path = icon_path.with_stem(new_icon_name)
        cls.set_start_icon(new_path)

    @classmethod
    def get_start_icon(cls):
        script_path = Path.script_templates / "getStartIcon.js"
        icon_path_str = cls.run_kde_script(script_path.text)
        return Path(icon_path_str)

    @classmethod
    def set_start_icon(cls, path):
        script_path = Path.script_templates / "setStartIcon.js"
        script = script_path.text.replace("ICON_PATH", str(path))
        cls.run_kde_script(script)


def restart(name):
    cli.capture_output(f"wmctrl -c {name}")

    # wait until closed
    while cli.capture_output("xdotool search --onlyvisible", name, check=False):
        time.sleep(0.5)

    cli.launch(name)


def apply_pycharm(name):
    letter = "d" if name == "dark" else "i"
    cli.run_commands(
        "jumpapp pycharm",
        f"xdotool key --clearmodifiers ctrl+shift+alt+y t Return {letter} Return",
    )


def apply_chromium(name):
    direction = "Left" if name == "light" else "Right"
    cli.run_commands(
        "jumpapp chromium",
        "sleep 1",
        "xdotool key ctrl+t",
        "xdotool type chrome://flags",
        "xdotool key Return",
        "sleep 0.5",
        "xdotool type dark",
        "xdotool key Return",
        "sleep 0.5",
        f"xdotool key --delay 10 Tab Tab Tab Tab Tab Tab {direction} Tab Return",
    )
