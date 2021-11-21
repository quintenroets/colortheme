import geocoder
import astral
from astral.sun import sun
from datetime import datetime
import time
import getpass

from libs.cli import Cli
from datetime import datetime

from .filemanager import FileManager

def main():
    while True:
        check_theme()

def check_theme():
    location = geocoder.ip("me").current_result.raw
    location_info = astral.LocationInfo(location["city"], location["region"], location["country"])
    sun_info = sun(location_info.observer)
    
    dawn = sun_info["dawn"].replace(tzinfo=None)    
    dusk = sun_info["dusk"].replace(tzinfo=None)
        
    settings = FileManager.load("settings")
    daytime = settings
        
    while daytime == settings:
        now = datetime.now()
        daytime = dawn < now and now < dusk
        daytime = "light" if daytime else "dark"
        if daytime == settings:
            time.sleep(5)
    
    if daytime == "light":
        go_light()
    elif daytime == "dark":
        go_dark()
    
def go_light():
    change_colortheme("dark", "light")
    
def go_dark():
    change_colortheme("light", "dark")
    
def change_colortheme(old, new):
    programs = ["chromium", "pycharm", "dolphin", "kate"]
    open_programs = {p: Cli.get(f"xdotool search --onlyvisible {p}", check=False) for p in programs}
    
    if open_programs["chromium"]:
        close("chromium")
        
    Cli.get(
        f"konsave -f -s {old}",
        f"konsave -a $(konsave -l | grep {new} | cut -f1)"
    )
    
    #time.sleep(2)
        
    for program, opened in open_programs.items():
        if opened:
            if program != "chromium":
                close(program)
                time.sleep(0.5)
            Cli.run(program, wait=False)
    
    restartplasma()
    FileManager.save(new, "settings")
    
def close(name):
    Cli.get(f"xdotool search --onlyvisible {name} | xargs -i% wmctrl -i -c %")
    
def restartplasma():
    Cli.run(
        "plasmashell --replace",
        "kwin --replace",
        wait=False
        )
    
def save_light():
    if FileManager.load("settings") == "dark":
        save_theme("light")
    
def save_dark():
    if FileManager.load("settings") == "light":
        save_theme("dark")
    
def save_theme(name):
    Cli.run(
        f"konsave -f -s {name}",
        f"konsave -e $(konsave -l | grep {name} | cut -f1)"
        )
 
if __name__ == "__main__":
    main()
