import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta

import astral
import geocoder
from astral import sun


class SunHours:
    def __init__(self, location_info: astral.LocationInfo, date: datetime = None):
        dawn, dusk = (
            event(location_info.observer, date=date).timestamp()
            - time.localtime().tm_gmtoff  # convert to gtm time
            for event in (sun.dawn, sun.dusk)
        )
        buffer_minutes = 0  # 30
        buffer_time = timedelta(minutes=buffer_minutes).total_seconds()

        self.light: float = dawn - buffer_time  # light = dawn - 30 min
        self.dark: float = dusk + buffer_time  # dark = dusk + 30 min

    @property
    def next_event(self):
        return self.light if time.time() < self.light else self.dark


def get_sun_hours():
    result = geocoder.ip("me").current_result
    # fallback location when no internet or too many requests
    region = result.raw["region"] if result else "New York"
    location_info = astral.LocationInfo(name="Home", region=region)
    sun_hours = SunHours(location_info)

    now = time.time()

    if now > sun_hours.dark:  # get events for next day if already dark
        sun_hours = SunHours(location_info, date=datetime.now() + timedelta(days=1))
    return sun_hours


@dataclass
class EventChecker:
    on_light: Callable = None
    on_dark: Callable = None

    def start(self):
        while True:
            self.check_event()

    def check_event(self):
        hours = get_sun_hours()

        if hours.light < time.time() < hours.dark:
            if self.on_light:
                self.on_light()
        else:
            if self.on_dark:
                self.on_dark()

        next_event = hours.next_event
        while time.time() < next_event:
            time.sleep(5)
