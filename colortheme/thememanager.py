import time
from datetime import datetime, timedelta

import astral
import geocoder
from astral.sun import sun

import cli
import gui
from backup.profilemanager import ProfileManager
from libs.threading import Threads


class SunHours:
    def __init__(self, dawn, dusk):
        self.dawn = dawn
        self.dusk = dusk


class ThemeManager:
    @staticmethod
    def start_check_service():
        while True:
            ThemeManager.check_theme()

    @staticmethod
    def check_theme():
        now = datetime.now()
        sunhours = ThemeManager.sun_hours
        daytime = "light" if sunhours.dawn < now < sunhours.dusk else "dark"
        if daytime != ProfileManager.active_profile:
            ThemeManager.apply(daytime, ask_confirm=True)

        next_event = sunhours.dawn if now < sunhours.dawn else sunhours.dusk
        while datetime.now() < next_event:
            time.sleep(5)

    @classmethod
    @property
    def sun_hours(cls):
        result = geocoder.ip("me").current_result
        # fallback location when no internet or too many requests
        location = (
            result.raw
            if result
            else {"city": "Brugge", "region": "Flanders", "country": "BE"}
        )
        location_info = astral.LocationInfo(
            location["city"], location["region"], location["country"]
        )

        sunhours = ThemeManager.get_sun_info(location_info)
        now = datetime.now()
        if now > sunhours.dusk:  # get events for next day if already dark
            sunhours = ThemeManager.get_sun_info(
                location_info, date=now + timedelta(days=1)
            )
        return sunhours

    @staticmethod
    def get_sun_info(location_info, date=None):
        sun_info = sun(location_info.observer, date=date)

        dawn = sun_info["dawn"].replace(tzinfo=None) - timedelta(
            minutes=30
        )  # light = dawn - 30 min
        dusk = sun_info["dusk"].replace(tzinfo=None) + timedelta(
            minutes=30
        )  # dark = dusk + 30 min

        return SunHours(dawn, dusk)

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
