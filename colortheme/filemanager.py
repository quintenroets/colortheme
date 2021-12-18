from pathlib import Path

from libs.filemanager import FileManager as FileManagerLib

class FileManager(FileManagerLib):
    root = FileManagerLib.root / Path(__file__).parent.name
