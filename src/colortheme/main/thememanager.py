import time

import cli
from backup.backups import profile

from ..models import Path


class ThemeManager:
    @classmethod
    def restart_plasma(cls) -> None:
        cls.run_kde("refreshCurrentShell")
        cli.launch("kwin --replace")

    @classmethod
    def run_kde(cls, command: str, *options: str) -> str:
        full_command = (
            f"qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.{command}"
        )
        return cli.capture_output(full_command, *options)

    @classmethod
    def run_kde_script(cls, script: str) -> str:
        return cls.run_kde("evaluateScript", script)

    @classmethod
    def open_programs(cls) -> list[str]:
        def is_open(program: str) -> bool:
            return cli.completes_successfully("xdotool search --onlyvisible", program)

        programs = ["dolphin", "kate"]
        return [program for program in programs if is_open(program)]

    @classmethod
    def start_apply(cls, theme: str) -> None:
        profile.Backup().apply_profile(theme)
        cls.apply_desktop_image(theme)
        cls.apply_start_icon(theme)
        cls.restart_plasma()

    @classmethod
    def apply_desktop_image(cls, theme: str) -> None:
        image_path = cls.get_desktop_image()
        new_desktop_image_name = "background" if theme == "light" else "background_dark"
        new_path = image_path.with_stem(new_desktop_image_name)
        cls.set_desktop_image(new_path)

    @classmethod
    def get_desktop_image(cls) -> Path:
        script_path = Path.script_templates / "getWallpaper.js"
        image_path_str = cls.run_kde_script(script_path.text)
        return Path.from_uri(image_path_str)

    @classmethod
    def set_desktop_image(cls, path: Path) -> None:
        script_path = Path.script_templates / "setWallpaper.js"
        script = script_path.text.replace("IMAGE_PATH", path.as_uri())
        cls.run_kde_script(script)

    @classmethod
    def apply_start_icon(cls, theme: str) -> None:
        icon_path = cls.get_start_icon()
        new_icon_name = "start_menu" if theme == "light" else "start_menu_dark_theme"
        new_path = icon_path.with_stem(new_icon_name)
        cls.set_start_icon(new_path)

    @classmethod
    def get_start_icon(cls) -> Path:
        script_path = Path.script_templates / "getStartIcon.js"
        icon_path_str = cls.run_kde_script(script_path.text)
        return Path(icon_path_str)

    @classmethod
    def set_start_icon(cls, path: Path) -> None:
        script_path = Path.script_templates / "setStartIcon.js"
        script = script_path.text.replace("ICON_PATH", str(path))
        cls.run_kde_script(script)


def restart(name: str) -> None:
    cli.capture_output(f"wmctrl -c {name}")

    # wait until closed
    while cli.capture_output("xdotool search --onlyvisible", name, check=False):
        time.sleep(0.5)

    cli.launch(name)
