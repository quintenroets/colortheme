import time
from collections.abc import Callable
from dataclasses import dataclass

from .sun_hours import fetch_sun_hours


@dataclass
class EventChecker:
    on_light: Callable[..., None] | None = None
    on_dark: Callable[..., None] | None = None

    def start(self) -> None:
        while True:
            self.check_event()

    def check_event(self) -> None:
        hours = fetch_sun_hours()

        if hours.light < time.time() < hours.dark:
            if self.on_light:
                self.on_light()
        else:
            if self.on_dark:
                self.on_dark()

        next_event = hours.next_event
        while time.time() < next_event:
            time.sleep(5)
