# dependencies
import json, os, ctypes
import pygame as pg
#test

# project and library pathes
PATH = {
    "go": os.path.dirname(__file__),
    "sysimg": os.path.dirname(__file__) + "\\images",
    "root": os.getcwd(),
    "assets": os.getcwd() + "\\assets",
    "images": os.getcwd() + "\\assets\\images",
    "maps": os.getcwd() + "\\assets\\maps",
    "tilesets": os.getcwd() + "\\assets\\tilesets",
    "entities": os.getcwd() + "\\assets\\entities"
}
IMG = {
    "noimage": pg.image.load(PATH["sysimg"] + "\\noimage.png"),
    "windowbg": pg.image.load(PATH["sysimg"] + "\\bg01.png"),
    "windowicon": pg.image.load(PATH["sysimg"] + "\\ente.png")
}
RESOLUTIONS = {
    "1920x1080": (1920, 1080)
}

def prettyPrint(data, sort=False, tabs=4):
    """Pretty print dict."""
    if data.__class__ is dict:
        print(json.dumps(data, sort_keys=sort, indent=tabs))
    else:
        print("Nothing to pretty-print.")
