from .utils import (
    PATH,
    loadAssets,
    draw,
    getFrames
)
from .libs.zrect import ZRect
import pygame as pg

class Entity(pg.sprite.Sprite):
    """every form of ingame-agency will be based on this class."""
    def __init__(self, name):
        """."""
        # looking for a json-file to use as the config
        for each in loadAssets(PATH["entities"] + "\\" + name):
            if each["type"] == "player":
                self.config = each# dict
        # initializing the sprite
        pg.sprite.Sprite.__init__(self)
        # additional attributes
        self.rawimage = pg.image.load(# pygame surface
            self.config["filepath"] + "\\" + self.config["image"]
        )
        self.size = self.config["framesize"]# tuple
        self.frames = getFrames(self.rawimage, self.size)# list
        self.image = self.frames[0]# pygame surface
        self.rect = self.image.get_rect()# pygame rect
class Player(Entity):
    """representing a playable character."""
    def __init__(self, name):
        """."""
        Entity.__init__(self, name)
