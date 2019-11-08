# dependencies
from .utils import (
    LIBPATH,
    validateDict,
    getDisplay,
    draw
)
import sys
import pygame as pg

class Window:
    """pygame's window module with extended features."""
    default = {
        "size": (320, 240),
        "title": "NoTitle",
        "resizable": False,
        "icon": LIBPATH["windowicon"]
    }
    def __init__(self, config={}):
        """."""
        self.config = validateDict(config, self.default)# dict
        # pygame module initializing
        pg.init()

        self.title = self.config["title"]# str
        self.icon = self.config["icon"]# str / pygame surface
        self.clock = pg.time.Clock()# pygame.clock
        self.preffered_fps = 60# int
        # fps is getting updated by self.update()
        self.fps = 0# int

        self.display = getDisplay(# pygame surface
            self.config["size"],
            resizable = self.config["resizable"]
        )
        self.changeTitle(self.config["title"])
        self.changeIcon(self.icon)
    def update(self):
        """updates stuff at apps loop-end."""
        pg.display.update()
        self.clock.tick(self.preffered_fps)
        self.fps = int(self.clock.get_fps())
    def quit(self):
        """exits the app."""
        pg.quit()
        sys.exit()
    def draw(self, object, position=(0, 0)):
        """draw everything to the windows surface."""
        draw(object, self.display, position)
    def resize(self, size):
        """'size' needs to be a tuple."""
        self.display = getDisplay(# pygame surface
            size,
            resizable = self.config["resizable"]
        )
    def getEvents(self):# pygame.event
        """pygame events"""
        events = []
        for event in pg.event.get():
            # quit application
            if event.type is pg.QUIT or (event.type is pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
            # resizing the window
            if event.type is pg.VIDEORESIZE:
                self.resize(event.size)
            # going fullscreen
            if event.type is pg.KEYDOWN and event.key == pg.K_F12:
                pass
            events.append(event)
        return events
    def pressedKeys(self):
        """return pygame-event's pressed-keys."""
        return pg.key.get_pressed()
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
