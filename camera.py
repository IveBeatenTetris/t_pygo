from .utils import (
    validateDict,
    getAnchors
)
import pygame as pg

class Camera(pg.Rect):
    """
    update the camera with each tick. if the camera tracks a target its
    coordinates are beeing recalculated here. call it with every game-loop.
    """
    default = {
        "size": (640, 480),
        "position": (0, 0),
        "tracking": None,
        "zoom": 1
    }
    def __init__(self, config={}):
        """
        'config' validated dict of properties to feed the camera with.
        'tracking' possible tracking of an entity. the camera then recalculates
            its position in the 'update()'-method.
        'zoomfactor' right now is only a placeholder for upcoming changes.
        'anchors' is used for quick-pointing a part of the rect. for example:
            draw(object, self, self.anchors["midcenter"]).
        """
        # comparing the defaults to the given one and create a new verified one
        self.config = validateDict(config, self.default)# dict
        # initiating rect
        pg.Rect.__init__(self, self.config["position"], self.config["size"])
        # additional attributes
        self.tracking = self.config["tracking"]# none / entity
        self.zoomfactor = self.config["zoom"]# int
        # sizing
        self.anchors = getAnchors(self.size)# dict
    def update(self):
        """."""
        if self.tracking:
            self.left = -(self.tracking.rect.center[0] - int(self.width / 2))
            self.top = -(self.tracking.rect.center[1] - int(self.height / 2))
