import sys

from libs.errorhandler import ErrorHandler

from .thememanager import ThemeManager

def main():
    args = sys.argv[1:]
    for theme in ["light", "dark"]:
        if theme in args:
            ThemeManager.apply(theme)
            
    if not args:
        while True:
            ThemeManager.check_theme()

def go_dark():
    ThemeManager.apply("dark")

def go_light():
    ThemeManager.apply("light")

def restartplasma():
    ThemeManager.restartplasma()

if __name__ == "__main__":
    with ErrorHandler():
        main()
