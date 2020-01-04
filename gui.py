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
# initiate pygame
pg.init()
# overall functions for use in the whole script
def loadXMLInterface(name):
    """."""
    for cfg in u.loadAssets(u.PATH["interface"] + "\\" + name):
        if cfg["type"] == "interface":
            return cfg
class App:
    """
    pygames window module with extended features. can be accessed by calling
        'globals()["app"]'.
    for the active event list use the internal one instead of calling the
        method 'events()' again to refresh events:
        'globals()["app"]._events' good.
        'globals()["app"].events()' bad.

    'defaults' is a dict of standard properties. on initiation the given
        parameter 'config' is beeing compared to the default dict. if some given
        properties are missing they are simply replaced with default values.
        the result is a validated dict to draw initiation instructions.
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
        """
        act as a pygame.display-window.

        'config' validated dict by comparison of a user set dict of properties
            and the elements default ones.
        'size' window size in a tuple for short reference only.
        'title' is gonna be displayed as the windows title.
        'icon' is displayed next to the title in the window.
        'clock' pygame clock for tracking fps.
        'preffered_fps' user defined maximal frames per second.
        'fps' is gonna be updated from the windows update-method.
        'paused' is a switch for showing a gui and closing it. handled by
            'self.pause()'.
        'mode' is for switching trough modes like 'moving' or 'paused'.
        'mouse' all information about mouse events are stored within here.
        'controller' decided to put it into the window. its been updated in the
            'window.events()'-method.
        'display' holds the actual pygame window.
        'screenshot' this surface can be used to simulate frozen screens like
            in menus. its refreshed by calling 'self.screenShot()'
        'fullscreen' if 'true' it renders the window maximized and borderless.
        'bgrepeat' str with either 'x' 'y' or 'xy'.
        'background' used to draw to background. might be 'str' or 'tuple'. if
            'string' then use it as image path and load a pygame.image surface.
        '_events' with each game-loop this list will become the new
            pygame.events. use this instead of calling 'app.events()'. this
            would only refresh the event list. resulting in loss of some events.
        """
        # centering window
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        # creating a dict based of comparison of config{} and default{}
        self.config = u.validateDict(config, self.default)# dict
        # additional attributes
        self.size = self.config["size"]# tuple
        self.title = self.config["title"]# str
        self.icon = self.config["icon"]# str / pygame.surface
        self.clock = pg.time.Clock()# pygame.clock
        self.preffered_fps = self.config["fps"]# int
        self.fps = 0# int
        self.paused = False# bool
        self.mode = "moving"# str
        self.mouse = Mouse()# mouse object
        self.controller = Controller()# controller (pygame.joystick.joystick)
        # display related stuff
        self.display = u.getDisplay(# pygame.surface
            self.config["size"],
            resizable = self.config["resizable"]
        )
        self.screenshot = None# none / pygame.surface
        self.changeTitle(self.config["title"])
        self.changeIcon(self.icon)
        # background related
        self.fullscreen = self.config["fullscreen"]# bool
        self.bgrepeat = self.config["backgroundrepeat"]# str
        self.background = self.__createBackground(# pygame.surface
            self.config["background"]
        )
        # event related
        self._events = []# list
        # adding app to globals for accessing out of boundaries
        globals()["app"] = self
    # game routines
    def update(self):
        """
        call this method on each main loop end to refresh its contents and
            visuals.
        """
        # refreshing display
        pg.display.update()
        # updating fps
        self.clock.tick(self.preffered_fps)
        self.fps = int(self.clock.get_fps())
    def quit(self):
        """exits the app."""
        pg.quit()
        sys.exit()
    def pause(self):
        """
        pauses the game or continues it. also freezes screen to simulate
            stopping by taking a display copied surface. internal property
            'self.paused' is gonna be togled on/off.
        """
        if self.paused is True:
            self.paused = False
        else:
            self.paused = True
            # make a screenshot
            self.screenshot = self.display.copy()
    # display stuff
    def __createBackground(self, bg):# pygame.surface
        """creates background based on background properties."""
        # declaring background type
        if type(bg) is str:
            bg = pg.image.load(bg)
        elif type(bg) is tuple:
            pass
        # checking background repeat
        if type(bg) is pg.Surface:
            if self.config["backgroundrepeat"]:
                # creating surfact with repeated background
                # 'bgrepeat' is the indicator ('x', 'y', 'xy')
                bg = u.repeatBG(
                    bg,
                    self.size,
                    self.bgrepeat
                )

        return bg
    def draw(self, object, position=(0, 0)):
        """draw something to windows 'display' surface."""
        u.draw(object, self.display, position)
    def resize(self, size=None):# bool
        """
        resizes the window.

        'size' needs to be a tuple. if no 'size parameter' is given this method
            serves as a 'resized-event' checker and returns 'true' or 'false'.
        """
        # on given parameter
        if size:
            # make new display surface
            self.display = u.getDisplay(# pygame.surface
                size,
                resizable = self.config["resizable"],
                fullscreen = self.fullscreen
            )
            # drawing background
            self.draw(self.background)
            # overwriting internal size (only for referencing)
            self.size = size
        # with no given parameter
        else:
            # return a tuple when resized or not
            resized = None

            for e in self._events:
                if e.type is pg.VIDEORESIZE:
                    resized = e.size

            return resized
    def screenShot(self, surface=None):# pygame.surface
        """
        makes a visual copy of the actual display and stores it in
            'self.screenshot'.
        if 'surface' is given then sotre a copy of that instead.
            """
        if surface:
            self.screenshot = surface.copy()
        else:
            self.screenshot = self.display.copy()

        return self.screenshot
    # event related methodes
    def events(self):# list
        """
        going trough some pygame events and returns a list of all active events.
        also updates the controller with events.
        """
        events = []
        keys = self.pressedKeys()

        # keyboard and mouse events
        for event in pg.event.get():
            # quit application
            if event.type is pg.QUIT:
                self.quit()
            if keys[pg.K_LALT] and keys[pg.K_F4]:
                self.quit()
            # resizing the window
            if event.type is pg.VIDEORESIZE:
                self.resize(event.size)
            # going fullscreen
            if event.type is pg.KEYDOWN and event.key is pg.K_F12:
                pass
            # finalizing event list
            events.append(event)

        # applying these events to the window-event list
        self._events = events
        # updating mouse object with pygame.events
        self.mouse.update(events)
        # updating controller element if there is one
        if self.controller.joystick:
            self.controller.update(events)

        return events
    def pressedKeys(self):# list
        """return pygame-event's pressed keys (list)."""
        return pg.key.get_pressed()
    def keys(self):# dict
        """might look for a more efficient way to check for pressed keys."""
        keys = {
            "return": False,
            "esc": False,
            "alt": False,
            "e": False,
            "f1": False,
            "f4": False
        }

        for event in self._events:
            if event.type is pg.KEYDOWN and event.key == pg.K_RETURN:
                keys["return"] = True
            if event.type is pg.KEYDOWN and event.key == pg.K_ESCAPE:
                keys["esc"] = True
            if event.type is pg.KEYDOWN and event.key == pg.K_LALT:
                keys["alt"] = True
            if event.type is pg.KEYDOWN and event.key == pg.K_F1:
                keys["f1"] = True
            if event.type is pg.KEYDOWN and event.key == pg.K_F4:
                keys["f4"] = True
            if event.type is pg.KEYDOWN and event.key == pg.K_e:
                keys["e"] = True

        return keys
    def mouseWheel(self):# str
        """mouse wheel event checking. returns 'none' or str ('up', 'down')."""
        wheel = None

        for event in self._events:
            if event.type is pg.MOUSEBUTTONDOWN and event.button == 4:
                wheel = "up"
            elif event.type is pg.MOUSEBUTTONDOWN and event.button == 5:
                wheel = "down"

        return wheel
    # window appearance
    def changeIcon(self, path):
        """create an icon for the window from an image."""
        if type(path) is pg.Surface:
            icon = path
        elif type(path) is str:
            icon = pg.image.load(path)

        icon = pg.transform.scale(icon, (32, 32))
        pg.display.set_icon(icon)
    def changeTitle(self, title):
        """change the window title. 'title' should be a string."""
        if type(title) is not str:
            title = str(title)
        pg.display.set_caption(title)
class GuiMaster(pg.Surface):
    """resembles a 'pygame.surface' but with advanced operations."""
    def __init__(self,
        size = (300, 200),
        position = (0, 0),
        background = (45, 45, 55)
    ):
        pg.Surface.__init__(self, size, pg.SRCALPHA)
        self.rect = self.get_rect()
        self.rect.topleft = position
        if background:
            self.fill(background)
class Interface(GuiMaster):
    """a screen to draw all gui elements to."""
    def __init__(self, name):
        cfg = loadXMLInterface(name)
        GuiMaster.__init__(self)
