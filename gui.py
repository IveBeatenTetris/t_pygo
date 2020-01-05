"""
this file contains all elements used to fuse a visual graphical user interface.
it starts of with 'GuiMaster' which serves as a master class for all / most of
the gui-elements.
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
    already converted to a readable dict.
    """
    for cfg in u.loadAssets(u.PATH["interface"] + "\\" + name):
        if cfg["type"] == "interface":
            return cfg
# first step to creating a pygame window
class App:
    """
    pygames-window-module with extended features. can be accessed by calling
    'globals()["app"]'.

    'defaults' is a dict of standard properties. on init, the given parameter
        'config' is beeing compared to the default dict. if some given
        properties are missing, they are simply replaced by default values.
        the result is a validated dict to draw initialisation instructions.
        it also declares what arguments can be passed to the app-object.
    """
    default = {
        "size": (320, 240),
        "title": "No Title",
        "resizable": False,
        "fullscreen": False,
        "background": u.LIBPATH["windowbg"],
        "background_repeat": None,
        "icon": u.LIBPATH["windowicon"],
        "fps": 30
    }
    def __init__(self, **kwargs):
        """
        inits pygame to act as an app-window.

        'config' validated 'dict' of comparing a user-set dict of properties
            with this object's default values.
        'display' holds the actual 'pygame.display.surface' object.
        'clock' pygame.clock for tracking 'fps'.
        'preffered_fps' user-defined maximal frames per second.
        'fps' is gonna be updated by the window's 'update()'-method.
        """
        self.config = u.validateDict(kwargs, self.default)
        # pygame init and window centering
        pg.init()
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        # creating display surface
        self.display = u.getDisplay(
            self.config["size"],
            resizable = self.config["resizable"]
        )# fps settings
        self.clock = pg.time.Clock()
        self.preffered_fps = self.config["fps"]
        self.fps = 0# int
    @property
    def events(self):
        """checks for the most basic events and returns the pg-event-list."""
        events = pg.event.get()

        for evt in events:
            if evt.type is pg.QUIT:
                self.quit()
            elif evt.type is pg.VIDEORESIZE:
                self.resize(evt.size)

        return events

    def draw(self, object, rect=None):
        """blits a surface-object / gui-element to the app's surface."""
        if not rect: rect = (0, 0)
        self.display.blit(object, rect)
    def resize(self, size):
        """resizes the app's surface."""
        self.display = u.getDisplay(
            size,
            resizable = self.config["resizable"]
        )
    def quit(self):
        """exits the app."""
        pg.quit()
        sys.exit()
    def update(self):
        """."""
        # refreshing display visuals
        pg.display.update()
        # updating fps
        self.clock.tick(self.preffered_fps)
        self.fps = int(self.clock.get_fps())
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
        """."""
        self.config = u.validateDict(kwargs, self.defaults)
        self.background = self.config["background"]
        self.rect = pg.Rect(self.config["position"], self.config["size"])
        self.resize(self.config["size"])
    def drawBackground(self):
        """."""
        if self.background:
            if type(self.background) is list or type(self.background) is tuple:
                self.fill(self.background)
    def resize(self, size):
        """."""
        pg.Surface.__init__(self, size, pg.SRCALPHA)
        self.rect.size = size
        self.drawBackground()
