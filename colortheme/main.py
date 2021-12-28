import argparse

from libs.cli import Cli
from libs.errorhandler import ErrorHandler

from .thememanager import ThemeManager


def main(action=None):
    with ErrorHandler():
        _main(action=action)


def _main(action=None):
    parser = argparse.ArgumentParser(description='Colortheme actions')
    parser.add_argument('action', nargs='?', help='The action to do [check[default], dark, light, restart]', default="check")
    args = parser.parse_args()
    if action is not None:
        args.action = action
    
    if args.action == "check":
        ThemeManager.start_check_service()
    elif args.action == "restart":
        ThemeManager.restartplasma()
    else:
        ThemeManager.apply(args.action)


def go_dark():
    main("dark")


def go_light():
    main("light")


def restartplasma():
    main("restart")


if __name__ == "__main__":
    main()
