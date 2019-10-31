# dependencies
from .utils import (
    validateDict,
    getDisplay,
    draw
)
import sys
import pygame as pg

class Window:
    """pygame's window module with extened features."""
    default = {
        "size": (320, 240),
        "resizable": False
    }
    def __init__(self, config={}):
        """."""
        self.config = validateDict(config, self.default)# dict
        # pygame module init
        pg.init()

        self.display = getDisplay(# pygame surface
            self.config["size"],
            resizable = self.config["resizable"]
        )
        self.clock = pg.time.Clock()# pygame.clock
        self.fps = 60# int
    def update(self):
        """updates stuff at apps loop-end."""
        pg.display.update()
        self.clock.tick(self.fps)
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
    def getEvents(self):
        """return pygame.events."""
        for event in pg.event.get():
            if event.type is pg.QUIT or (
                event.type is pg.KEYDOWN and
                event.key == pg.K_ESCAPE
            ):
                self.quit()
            if event.type is pg.VIDEORESIZE:
                pass
