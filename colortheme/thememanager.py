import time

import cli
import gui
from backup.profilemanager import ProfileManager
from libs.threading import Threads

from .eventchecker import EventChecker


class ThemeManager:
    @staticmethod
    def start_check_service():
        EventChecker(
            on_light=ThemeManager.on_light, on_dark=ThemeManager.on_dark
        ).start()

    @staticmethod
    def on_light():
        ThemeManager.check_theme("light")

    @staticmethod
    def on_dark():
        ThemeManager.check_theme("dark")

    @staticmethod
    def check_theme(name):
        if ProfileManager.active_profile != name:
            ThemeManager.apply(name, ask_confirm=True)

    @staticmethod
    def apply(name, ask_confirm=False):
        programs = ["pycharm", "dolphin", "kate", "chromium"]
        open_programs = [
            p
            for p in programs
            if cli.get("xdotool search --onlyvisible", p, check=False)
        ]
        confirmed = (
            not ask_confirm
            or not any(open_programs)
            or gui.ask_yn(f"Change to {name} theme?")
        )
        if confirmed:
            ThemeManager.start_apply(name, open_programs)

        return confirmed

    @staticmethod
    def start_apply(theme, open_programs):
        custom_apply_mapping = {
            "chromium": ThemeManager.apply_chromium,
            "pycharm": ThemeManager.apply_pycharm,
        }
        custom_apply = set({})
        for program, function in custom_apply_mapping.items():
            if program in open_programs:
                open_programs.remove(program)
                custom_apply.add(function)

        ProfileManager.apply(theme)
        ThemeManager.restartplasma()
        Threads(ThemeManager.restart, args=(open_programs,)).start().join()

        for custom in custom_apply:
            time.sleep(2)
            custom(theme)

    @staticmethod
    def restart(name):
        cli.get(f"wmctrl -c {name}")

        # wait until closed
        while cli.get("xdotool search --onlyvisible", name, check=False):
            time.sleep(0.5)

        cli.start(name)

    @staticmethod
    def restartplasma():
        cli.run_commands("plasmashell --replace", "kwin --replace", wait=False)

    @staticmethod
    def apply_pycharm(name):
        letter = "d" if name == "dark" else "i"
        cli.run_commands(
            "jumpapp pycharm",
            f"xdotool key --clearmodifiers ctrl+shift+alt+y t Return {letter} Return",
        )

    @staticmethod
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
