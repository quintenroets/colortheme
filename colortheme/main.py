import argparse

from . import thememanager


def main(action=None):
    parser = argparse.ArgumentParser(description="Colortheme actions")
    parser.add_argument(
        "action",
        nargs="?",
        help="The action to do [check[default], dark, light, restart]",
        default="check",
    )
    args = parser.parse_args()
    if action is not None:
        args.action = action

    if args.action == "check":
        thememanager.start_check_service()
    elif args.action == "restart":
        thememanager.restartplasma()
    else:
        thememanager.apply(args.action)


def go_dark():
    main("dark")


def go_light():
    main("light")


def restartplasma():
    main("restart")


if __name__ == "__main__":
    main()
