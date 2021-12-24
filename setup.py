from setuptools import setup, find_packages

NAME = "colortheme"

def read(filename):
    try:
        with open(filename) as fp:
            content = fp.read().split("\n")
    except FileNotFoundError:
        content = []
    return content

setup(
    author="Quinten Roets",
    author_email="quinten.roets@gmail.com",
    description='',
    name=NAME,
    version='1.0',
    packages=find_packages(),
    install_requires=read("requirements.txt"),
    entry_points={
        "console_scripts": [
            "colorthemechecker = colortheme.starter:main",
            "light = colortheme.starter:go_light",
            "dark = colortheme.starter:go_dark",
            "restartplasma = colortheme.starter:restartplasma",
            ]
        },
)
