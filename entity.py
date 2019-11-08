from .utils import (
    PATH,
    loadAssets,
    draw,
    getFrames
)
from .libs.zrect import ZRect
import pygame as pg

class Entity(pg.sprite.Sprite):
    """
    every form of ingame-agency will be based on this class. 'name' should be
    asset-name.
    """
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
    def position(self, pos=(0, 0)):
        """reposition of the entity sprite. updates the rect."""
        if type(pos) is pg.Rect:
            self.rect.topleft = pos.topleft
        elif type(pos) is tuple:
            self.rect.topleft = pos
    def move(self, x=0, y=0):
        """move the entity to the given coordinates."""
        self.position((
            self.rect.left + x,
            self.rect.top + y
        ))
class Player(Entity):
    """representing a playable character."""
    def __init__(self, name):
        """."""
        Entity.__init__(self, name)
