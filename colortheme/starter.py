import sys

from .thememanager import ThemeManager

def main():
    args = sys.argv[1:]
    for theme in ["light", "dark"]:
        if theme in args:
            ThemeManager.change_colortheme(theme)
        elif f"save{theme}" in args:
            ThemeManager.save_theme(theme)

def go_dark():
    ThemeManager.change_colortheme("dark")

def go_light():
    ThemeManager.change_colortheme("light")

def save_light():
    ThemeManager.save_theme("light")

def save_dark():
    ThemeManager.save_theme("dark")

def restartplasma():
    ThemeManager.restartplasma()

if __name__ == "__main__":
    main()