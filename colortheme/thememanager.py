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
        programs = ["chromium", "pycharm", "dolphin", "kate"]
        if confirm and False:
            programs.append("konsole")

        open_programs = [p for p in programs if Cli.get(f"xdotool search --onlyvisible {p}", check=False)]
        confirmed = (
            not ask_confirm
            or not any(open_programs)
            or Gui.ask_yn(f"Change to {new} theme?")
        )
        if confirmed:
            ThemeManager.start_apply(name, open_programs)

        return confirmed

    @staticmethod
    def start_apply(name, open_programs):
        if "chromium" in open_programs:
            ThemeManager.close("chromium")

        ProfileManager.apply(name)
        ThemeManager.restartplasma()
        Threads(ThemeManager.close, open_programs).join()
        # qdbus org.kde.KWin /KWin reconfigure  -> reload title bars for applications

        if "pycharm" in open_programs:
            time.sleep(1.5)
            open_programs.remove("pycharm")
            open_programs.append("pycharm-professional")

        Threads(Cli.run, open_programs, wait=False).join()
        FileManager.save(new, "settings")

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
 
if __name__ == "__main__":
    main()
