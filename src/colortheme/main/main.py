from backup.backups import profile

from .eventchecker import EventChecker
from .thememanager import ThemeManager


def main() -> None:
    """
    Start colortheme check service.
    """
    checker = EventChecker(
        on_light=lambda: check_theme("light"),
        on_dark=lambda: check_theme("dark"),
    )
    checker.start()


def check_theme(name: str) -> None:
    if profile.Backup().active_profile != name:
        apply(name, ask_confirm=True)


def apply(name: str, *, ask_confirm: bool = False) -> bool:
    confirmed = not ask_confirm
    if confirmed:
        ThemeManager.start_apply(name)

    return confirmed
