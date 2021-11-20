from . import constants
from libs.filemanager import FileManager as FileManagerLib

class FileManager(FileManagerLib):
    root = constants.ASSETS_PATH

