"""
this file contains all elements used to fuse a visual graphical user interface.
it starts of with 'GuiMaster' which serves as a master class for all / most of
the elements.
"""
# dependencies
import pygame as pg
import os, sys
from . import utils as u
from .input import Controller, Mouse
# overall functions to pick from
def loadXMLInterface(name):
    """
    returns an interface structure written in a markup language. the output is
    already converted to a readable 'dict'.
    """
    for cfg in u.loadAssets(u.PATH["interface"] + "\\" + name):
        if cfg["type"] == "interface":
            return cfg
# first step to creating a pygame window
class App:
    """
    pygames window module with extended features. can be accessed by calling
    'globals()["app"]'.
    """
    default = {
        "size": (320, 240),
        "title": "No Title",
        "resizable": False,
        "fullscreen": False,
        "background": u.LIBPATH["windowbg"],
        "backgroundrepeat": None,
        "icon": u.LIBPATH["windowicon"],
        "fps": 30
    }
    def __init__(self, config={}):
        pg.init()
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        self.config = u.validateDict(config, self.default)# dict
    def update(self):
        pass
class GuiMaster(pg.Surface):
    """
    resembles a 'pygame.surface' but with advanced operations.

    'defaults' serves as a setup-dict to evaluate building instructions for the
        master-element.
    """
    defaults = {
        "size": (300, 200),
        "position": (0, 0),
        "background": (45, 45, 55)
    }
    def __init__(self, **kwargs):
        self.config = u.validateDict(kwargs, self.defaults)
        self.background = self.config["background"]
        self.rect = pg.Rect(self.config["position"], self.config["size"])
        self.resize(self.config["size"])
    def drawBackground(self):
        if self.background:
            if type(self.background) is list or type(self.background) is tuple:
                self.fill(self.background)
    def resize(self, size):
        pg.Surface.__init__(self, size, pg.SRCALPHA)
        self.rect.size = size
        self.drawBackground()
