import geocoder
import astral
from astral.sun import sun
from datetime import datetime
import time
import getpass

from backup.profilemanager import ProfileManager

from libs.cli import Cli
from libs.gui import Gui
from libs.threading import Threads
from datetime import datetime, timedelta

class ThemeManager:
    @staticmethod
    def start_check_service():
        while True:
            ThemeManager.check_theme()
    
    @staticmethod
    def check_theme():
        dawn, dusk = ThemeManager.get_sun_events()
        settings = ProfileManager.get_active()
        daytime = settings

        while daytime == settings:
            now = datetime.now()
            if now.date() > dusk.date():
                # recalculate event if already next day
                dawn, dusk = ThemeManager.get_sun_events()

            daytime = "light" if dawn < now < dusk else "dark"
            if daytime == settings:
                time.sleep(5)
            else:
                 # reload settings to make sure that theme has not been changed manually already
                settings = ProfileManager.get_active()

        applied = ThemeManager.apply(daytime, ask_confirm=True)

        if not applied:
            # wait until next event before checking again
            next_event = dawn if now < dawn else dusk
            while now < next_event:
                time.sleep(5)
                now = datetime.now()

    @staticmethod
    def get_sun_events():
        result = geocoder.ip("me").current_result
        # fallback location when no internet or too many requests
        location = result.raw if result else {'city': 'Brugge', 'region': 'Flanders', 'country': 'BE'}        
        location_info = astral.LocationInfo(location["city"], location["region"], location["country"])

        dawn, dusk = ThemeManager.get_sun_info(location_info)
        now = datetime.now()
        if now > dusk:
            # get events for next day if already dark
            dawn, dusk = ThemeManager.get_sun_info(location_info, date=now+timedelta(days=1))
        return dawn, dusk
    
    @staticmethod
    def get_sun_info(location_info, date=None):
        sun_info = sun(location_info.observer, date=date)

        dawn = sun_info["dawn"].replace(tzinfo=None) - timedelta(minutes=30) # light = dawn - 30 min
        dusk = sun_info["dusk"].replace(tzinfo=None) + timedelta(minutes=30) # dark = dusk + 30 min

        return dawn, dusk

    @staticmethod
    def apply(name, ask_confirm=False):
        programs = ["pycharm", "dolphin", "kate"] # chromium
        if ask_confirm and False:
            programs.append("konsole")

        open_programs = [p for p in programs if Cli.get(f"xdotool search --onlyvisible {p}", check=False)]
        confirmed = (
            not ask_confirm
            or not any(open_programs)
            or Gui.ask_yn(f"Change to {name} theme?")
        )
        if confirmed:
            ThemeManager.start_apply(name, open_programs)

        return confirmed

    @staticmethod
    def start_apply(name, open_programs):
        if "chromium" in open_programs:
            ThemeManager.close("chromium")

        if "pycharm" in open_programs:
            open_programs.remove("pycharm")
            ThemeManager.apply_pycharm(name)

        ProfileManager.apply(name)
        ThemeManager.restartplasma()
        Threads(ThemeManager.close, open_programs).join()
        Threads(Cli.run, open_programs, wait=False).join()

    @staticmethod
    def close(name):
        Cli.get(f"xdotool search --onlyvisible {name} | xargs -i% wmctrl -i -c %")
        time.sleep(0.5)
        # wait until closed
        while Cli.get(f"xdotool search --onlyvisible {name}", check=False):
            time.sleep(0.5)

    @staticmethod
    def restartplasma():
        Cli.run("plasmashell --replace", "kwin --replace", wait=False)

    @staticmethod
    def apply_pycharm(name):
        letter = "d" if name == "dark" else "i"
        Cli.run(
            "jumpapp pycharm",
            f"xdotool key --clearmodifiers ctrl+shift+alt+y t Return {letter} Return"
        )
