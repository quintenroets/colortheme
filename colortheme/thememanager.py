import geocoder
import astral
from astral.sun import sun
from datetime import datetime
import time
import getpass

from libs.cli import Cli
from libs.gui import Gui
from libs.threading import Threads
from datetime import datetime, timedelta

from .filemanager import FileManager

class ThemeManager:
    @staticmethod
    def check_theme():
        dawn, dusk = ThemeManager.get_sun_events()
        settings = ThemeManager.get_theme()
        daytime = settings

        while daytime == settings:
            now = datetime.now()
            if now.date() > dusk.date():
                # recalculate event if already next day
                dawn, dusk = ThemeManager.get_sun_events()

            daytime = "light" if dawn < now < dusk else "dark"
            if daytime == settings:
                time.sleep(5)
        
        ThemeManager.change_colortheme(daytime, confirm=True)

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
    def change_colortheme(new, confirm=False):
        old = "dark" if new == "light" else "light"
        if ThemeManager.get_theme() == old:
            programs = ["chromium", "pycharm", "dolphin", "kate"]
            if confirm and False:
                programs.append("konsole")
            open_programs = [p for p in programs if Cli.get(f"xdotool search --onlyvisible {p}", check=False)]
            canceled = (
                confirm and
                any(open_programs) and
                not Gui.ask_yn(f"Change to {new} theme?")
            )
            if canceled:
                now = datetime.now()
                dawn, dusk = ThemeManager.get_sun_events()
                next_event = dawn if now < dawn else dusk
                while now < next_event:
                    time.sleep(5)
                    now = datetime.now()
                # dont change colortheme if not confirmed
                # and dont ask again until next event
            else:
                ThemeManager.start_colortheme_change(old, new, open_programs)

    @staticmethod
    def start_colortheme_change(old, new, open_programs):
        if "chromium" in open_programs:
            ThemeManager.close("chromium")

        ThemeManager.change_config(old, new)
        ThemeManager.restartplasma()
        Threads(ThemeManager.close, open_programs).join()

        if "pycharm" in open_programs:
            time.sleep(1.5)
            open_programs.remove("pycharm")
            open_programs.append("pycharm-professional")

        Threads(Cli.run, open_programs, wait=False).join()
        FileManager.save(new, "settings")

    @staticmethod
    def change_config(old, new):
        Cli.get(
            f"konsave -f -s {old}",
            f"konsave -a $(konsave -l | grep {new} | cut -f1)"
        )

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
    def save_theme(name):
        if ThemeManager.get_theme() == name:
            Cli.run(
                f"konsave -f -s {name}",
                f"konsave -e $(konsave -l | grep {name} | cut -f1)"
                )

    @staticmethod
    def get_theme():
        theme = FileManager.load("settings")
        if not theme: # use default theme if not present
            theme = "light"
        return theme
 
if __name__ == "__main__":
    main()
