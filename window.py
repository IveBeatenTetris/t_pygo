from .utils import (
    LIBPATH,
    validateDict,
    getDisplay,
    draw
)
from .controller import Controller
import pygame as pg
import sys

class Window:
    """pygames window module with extended features."""
    default = {
        "size": (320, 240),
        "title": "No Title",
        "resizable": False,
        "icon": LIBPATH["windowicon"],
        "fps": 30
    }
    def __init__(self, config={}):
        """
        initiates pygame to act as a pygame-window.
        'title' is gonna be displayed as the windows title.
        'icon' is displayed next to the title in the window.
        'preffered_fps' - its in the name.
        'fps' is gonna be updated from the windows update-method.
        'paused' is a switch for showing a gui and closing it. handled by
            'self.pause()'.
        'mode' is for switching trough modes like 'moving' or 'paused'.
        'controller' decided to put it into the window. its been updated in the
        'window.events()'-method.
        '_events' with each game-loop this list will become the new
            pygame.events.
        'display' holds the actual pygame window.
        'screenshot' this surface can be used to simulate frozen screens like
            in menus.
        'size' window size in a tuple for short reference.
        """
        pg.init()
        self.config = validateDict(config, self.default)# dict
        # additional attributes
        self.title = self.config["title"]# str
        self.icon = self.config["icon"]# str / pygame.surface
        self.clock = pg.time.Clock()# pygame.clock
        self.preffered_fps = self.config["fps"]# int
        self.fps = 0# int
        self.paused = False# bool
        self.mode = "moving"# str
        self.controller = Controller()# controller (pygame.joystick.joystick)
        self._events = []# list
        # display related stuff
        self.display = getDisplay(# pygame.surface
            self.config["size"],
            resizable = self.config["resizable"]
        )
        self.screenshot = self.display.copy()# pygame.surface
        self.size = self.config["size"]# tuple
        self.changeTitle(self.config["title"])
        self.changeIcon(self.icon)
    # game routines
    def update(self):
        """updates stuff at apps loop-end."""
        pg.display.update()
        self.clock.tick(self.preffered_fps)
        self.fps = int(self.clock.get_fps())
    def quit(self):
        """exits the app."""
        pg.quit()
        sys.exit()
    def pause(self):
        """pauses the game or continues it."""
        if self.paused is True:
            self.paused = False
        else:
            self.paused = True
            # create a screenshot
            self.screenshot = self.display.copy()
    # display stuff
    def draw(self, object, position=(0, 0)):
        """draw everything to the windows surface."""
        draw(object, self.display, position)
    def resize(self, size):
        """'size' needs to be a tuple."""
        self.display = getDisplay(# pygame.surface
            size,
            resizable = self.config["resizable"]
        )
        self.size = size
    # event related methodes
    def events(self):# pygame.event
        """pygame events. updates the controller with events."""
        events = []
        # keyboard and mouse events
        for event in pg.event.get():
            # quit application
            if event.type is pg.QUIT:
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
        # updating controller element if there is one
        if self.controller.joystick:
            self.controller.update(events)

        return events
    def pressedKeys(self):
        """return pygame-event's pressed-keys."""
        return pg.key.get_pressed()
    def keys(self):
        """might look for a more efficient way to check for hitten keys."""
        keys = {
            "esc": False,
            "f1": False
        }

        for event in self._events:
            if event.type is pg.KEYDOWN and event.key == pg.K_ESCAPE:
                keys["esc"] = True
            if event.type is pg.KEYDOWN and event.key == pg.K_F1:
                keys["f1"] = True

        return keys
    def mouseWheel(self):
        """mouse wheel event checking. returns a string."""
        wheel = "none"

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
        """change the window-title. 'title' should be a string."""
        if type(title) is not str:
            title = str(title)
        pg.display.set_caption(title)
