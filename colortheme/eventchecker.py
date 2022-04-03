import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable

import astral
import geocoder
from astral import sun


class SunHours:
    def __init__(self, location_info: astral.LocationInfo, date: datetime = None):
        dawn, dusk = (
            event(location_info.observer, date=date).timestamp()
            for event in (sun.dawn, sun.dusk)
        )
        buffer_time = timedelta(minutes=30).total_seconds()

        self.light: float = dawn - buffer_time  # light = dawn - 30 min
        self.dark: float = dusk + buffer_time  # dark = dusk + 30 min

    @property
    def next_event(self):
        return self.light if time.time() < self.light else self.dark


def sun_hours():
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

    sunhours = SunHours(location_info)
    now = time.time()
    if now > sunhours.dark:  # get events for next day if already dark
        sunhours = SunHours(location_info, date=datetime.now() + timedelta(days=1))
    return sunhours


@dataclass
class EventChecker:
    on_light: Callable = None
    on_dark: Callable = None

    def start(self):
        while True:
            self.check_event()

    def check_event(self):
        sunhours = sun_hours()

        if sunhours.light < time.time() < sunhours.dark:
            if self.on_light:
                self.on_light()
        else:
            if self.on_dark:
                self.on_dark()

        next_event = sunhours.next_event
        while time.time() < next_event:
            time.sleep(5)
