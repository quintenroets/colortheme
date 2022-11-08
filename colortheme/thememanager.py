import time

import cli
import gui
from backup import profilemanager
from libs.threading import Threads

from .eventchecker import EventChecker


def start_check_service():
    EventChecker(
        on_light=lambda: check_theme("light"), on_dark=lambda: check_theme("dark")
    ).start()


def check_theme(name):
    if profilemanager.active_profile.name != name:
        apply(name, ask_confirm=True)


def apply(name, ask_confirm=False):
    programs = ["pycharm", "dolphin", "kate", "chromium"]

    def is_open(program: str):
        return cli.is_succes("xdotool search --onlyvisible", program)

    open_programs = [p for p in programs if is_open(p)]
    confirmed = (
        not ask_confirm
        or not any(open_programs)
        or gui.ask_yn(f"Change to {name} theme?")
    )
    if confirmed:
        start_apply(name, open_programs)

    return confirmed


def start_apply(theme, open_programs):
    custom_apply_mapping = {
        # "chromium": apply_chromium,
        "pycharm": apply_pycharm,
    }
    custom_apply = set({})
    for program, function in custom_apply_mapping.items():
        if program in open_programs:
            open_programs.remove(program)
            custom_apply.add(function)

    profilemanager.apply(theme)
    restartplasma()
    Threads(restart, args=(open_programs,)).start().join()

    for custom in custom_apply:
        time.sleep(2)
        custom(theme)


def restart(name):
    cli.get(f"wmctrl -c {name}")

    # wait until closed
    while cli.get("xdotool search --onlyvisible", name, check=False):
        time.sleep(0.5)

    cli.start(name)


def restartplasma():
    cli.run_commands("plasmashell --replace", "kwin --replace", wait=False)


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
