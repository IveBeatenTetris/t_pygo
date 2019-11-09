from .utils import (
    validateDict,
    draw,
    getAnchors
)
import pygame as pg

class Camera(pg.Surface):
    """."""
    # default values
    default = {
        "size": (640, 480),
        "position": (0, 0),
        "tracking": None,
        "zoomfactor": 1
    }
    def __init__(self, config={}):
        """."""
        self.config = validateDict(config, self.default)# dict
        self.tracking = self.config["tracking"]# none / entity
        self.zoomfactor = self.config["zoomfactor"]# int
        # initiating surface
        pg.Surface.__init__(self, self.config["size"], pg.SRCALPHA)
        # sizing
        self.rect = self.get_rect()# pygame rect
        self.anchors = getAnchors(self.rect.size)# dict
    def draw(self, object, position=(0,0)):
        """drawing something to the camera surface."""
        draw(object, self, position)
    def update(self):
        """update the camera with each tick."""
        if self.tracking:
            self.rect.left = -(self.tracking.rect.center[0] - int(self.rect.width / 2))
            self.rect.top = -(self.tracking.rect.center[1] - int(self.rect.height / 2))
