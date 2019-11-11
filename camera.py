from .utils import (
    validateDict,
    draw,
    getAnchors
)
import pygame as pg

class Camera(pg.Surface):
    """
    the camera is used for correctly draw everything to the window screen.
    one should use the camera as position agrument to draw a map, layer or
    just everything that's static and not really moving.
    """
    # default values
    default = {
        "size": (320, 240),
        "tracking": None,
        "zoomfactor": 1
    }
    def __init__(self, config={}):
        """
        'config' validated config file to feed the camera with.
        'tracking' possible tracking of an entity. the camera then recalculates
            its position in the 'update()'-method.
        'zoomfactor' right now is only a placeholder for upcoming changes.
        'anchors' is used for quick-pointing a part of the rect. for example:
            draw(object, self, self.anchors["midcenter"]).
        """
        # comparing the defaults to the given one and create a new verified one
        self.config = validateDict(config, self.default)# dict
        # additional attributes
        self.tracking = self.config["tracking"]# none / entity / pygame.srpite
        self.zoomfactor = self.config["zoomfactor"]# int
        # initiating surface
        pg.Surface.__init__(self, self.config["size"], pg.SRCALPHA)
        # sizing
        self.rect = self.get_rect()# pygame.rect
        self.anchors = getAnchors(self.rect.size)# dict
    def draw(self, object, position=(0,0)):
        """drawing something to the camera surface."""
        draw(object, self, position)
    def update(self):
        """
        update the camera with each tick. if the camera tracks a target its
        coordinates are beeing recalculated here. call it with every game-loop.
        """
        if self.tracking:
            self.rect.left = -(self.tracking.rect.center[0] - int(self.rect.width / 2))
            self.rect.top = -(self.tracking.rect.center[1] - int(self.rect.height / 2))
