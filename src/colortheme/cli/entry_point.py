from package_utils.context.entry_point import create_entry_point

from colortheme.main import main
from colortheme.main.thememanager import ThemeManager

from ..context import context

entry_point = create_entry_point(main.main, context)
restart_plasma = ThemeManager.restart_plasma


def go_light() -> None:
    main.apply("light")


def go_dark() -> None:
    main.apply("dark")
