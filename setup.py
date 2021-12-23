from setuptools import setup, find_packages

NAME = "colortheme"

def read(filename):
    try:
        with open(filename) as fp:
            content = fp.read().split("\n")
    except FileNotFoundError:
        content = []
    return content

from libs.cli import Cli

setup(
    author="Quinten Roets",
    author_email="quinten.roets@gmail.com",
    description='',
    name=NAME,
    version='1.0',
    packages=find_packages(),
    setup_requires=["libs @ git+https://@github.com/quintenroets/libs"],
    install_requires=read("requirements.txt"),
    entry_points={
        "console_scripts": [
            "colorthemechecker = colortheme.starter:main",
            "dark = colortheme.starter:go_dark",
            "light = colortheme.starter:go_light",
            "savelight = colortheme.starter:save_light",
            "savedark = colortheme.starter:save_dark",
            "restartplasma = colortheme.starter:restartplasma",
            ]
        },
)
