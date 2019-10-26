# dependencies
from .utils import (
    validateDict,
    getDisplay,
    draw
)
import pygame as pg

class Window:
    """
    pygame's window module with extened features.
    'default' declares what arguments are actually workable.
    """
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
    def draw(self, object, position=(0, 0)):
        """draw everything to the windows surface."""
        draw(object, self.display, position)
