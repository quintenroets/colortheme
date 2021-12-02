import geocoder
import astral
from astral.sun import sun
from datetime import datetime
import time
import getpass

from libs.cli import Cli
from datetime import datetime, timedelta

from .filemanager import FileManager

def main():
    while True:
        check_theme()

def check_theme():
    dawn, dusk = get_sun_events()
    settings = get_theme()
    daytime = settings
            
    while daytime == settings:
        now = datetime.now()
        if now.date() > dusk.date():
            # recalculate event if already next day
            dawn, dusk = get_sun_events()
        
        daytime = "light" if dawn < now < dusk else "dark"
        if daytime == settings:
            time.sleep(5)
    
    if daytime == "light":
        go_light()
    elif daytime == "dark":
        go_dark()
        
def get_sun_events():
    result = geocoder.ip("me").current_result
    # fallback location when no internet
    location = result.raw if result else {'city': 'Brugge', 'region': 'Flanders', 'country': 'BE'}
    location_info = astral.LocationInfo(location["city"], location["region"], location["country"])
    
    dawn, dusk = get_sun_info(location_info)
    now = datetime.now()
    if now > dusk:
        # get events for next day if already dark
        dawn, dusk = get_sun_info(location_info, date=now+timedelta(days=1))
    return dawn, dusk
    

def get_sun_info(location_info, date=None):
    sun_info = sun(location_info.observer, date=date)
    
    dawn = sun_info["dawn"].replace(tzinfo=None) - timedelta(minutes=30) # light = dawn - 30 min
    dusk = sun_info["dusk"].replace(tzinfo=None) + timedelta(minutes=30) # dark = dusk + 30 min
    
    return dawn, dusk
    
def go_light():
    if get_theme() == "dark":
        change_colortheme("dark", "light")
    
def go_dark():
    if get_theme() == "light":
        change_colortheme("light", "dark")
    
def change_colortheme(old, new):
    programs = ["chromium", "pycharm", "dolphin", "kate"]
    open_programs = {p: Cli.get(f"xdotool search --onlyvisible {p}", check=False) for p in programs}
    
    ask_confirmation = any(open_programs.values())
    if ask_confirmation:
        try:
            Cli.get(f"kdialog --yesno 'Change to {new} theme?'")
        except:
            return
            # dont change colortheme if not confirmed
    
    if open_programs["chromium"]:
        close("chromium")

    change_config(old, new)
            
    for program, opened in open_programs.items():
        if opened:
            if program != "chromium":
                close(program)
                sleep_time = 2 if program == "pycharm" else 0.5
                time.sleep(sleep_time)
            Cli.run(program, wait=False)
    
    restartplasma()
    FileManager.save(new, "settings")

def change_config(old, new):
    Cli.get(
        f"konsave -f -s {old}",
        f"konsave -a $(konsave -l | grep {new} | cut -f1)"
    )
    
def close(name):
    Cli.get(f"xdotool search --onlyvisible {name} | xargs -i% wmctrl -i -c %")
    
def restartplasma():
    Cli.run(
        "plasmashell --replace",
        "kwin --replace",
        wait=False
        )
    
def save_light():
    if get_theme() == "dark":
        save_theme("light")
    
def save_dark():
    if get_theme() == "light":
        save_theme("dark")
    
def save_theme(name):
    Cli.run(
        f"konsave -f -s {name}",
        f"konsave -e $(konsave -l | grep {name} | cut -f1)"
        )
    
def get_theme():
    return FileManager.load("settings")
 
if __name__ == "__main__":
    main()
