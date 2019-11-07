# dependencies
from .utils import (
    PATH,
    draw,
    getFrames,
    loadAssets
)
import pygame as pg

class Tile(pg.sprite.Sprite):
    """
    cut out a sprite from an image. actually its just replacement.
    """
    def __init__(self, config={}):
        """."""
        pg.sprite.Sprite.__init__(self)
        self.image = config["image"]# pygame surface
        self.rect = self.image.get_rect()# pygame rect
        self.id = config["id"]# int
        # additional attributes
        try:# str
            self.name = config["name"]
        except KeyError:
            self.name = "NoName"
        try:# bool
            self.block = config["block"]
        except KeyError:
            self.block = False
        try:# bool
            self.visible = config["visible"]
        except KeyError:
            self.visible = True
class Tileset(pg.Surface):
    """."""
    def __init__(self, name):
        """."""
        for each in loadAssets(PATH["tilesets"] + "\\" + name):
            if each["type"] == "tileset":
                self.config = each# dict

        self.name = self.config["name"]# str
        self.path = self.config["filepath"]# str
        self.image = pg.image.load(# pygame.surface
            self.path + "\\" + self.config["image"]
        )
        self.size = self.image.get_rect().size# tuple
        self.tilesize = (# tuple
            self.config["tilewidth"],
            self.config["tileheight"]
        )
        self.tiles = self.__createTiles()# list

        pg.Surface.__init__(self, self.size, pg.SRCALPHA)
        draw(self.image, self)
    def __createTiles(self):# list
        """return a list of all tiles in the given tileset-image."""
        tilelist = []

        for i, each in enumerate(getFrames(self.image, self.tilesize), 0):
            # this is food for a new tile object
            cfg = {
                "image": each,
                "id": i,
                }

            # additional tile properties
            if "tileproperties" in self.config:
                props = self.config["tileproperties"]
                if str(i) in props:

                    # tile passable?
                    try:
                        cfg["block"] = props[str(i)]["block"]
                    except KeyError:
                        pass
                    # tile visibility
                    try:
                        cfg["visible"] = props[str(i)]["visible"]
                    except KeyError:
                        pass
                    # tile name
                    try:
                        cfg["name"] = props[str(i)]["name"]
                    except KeyError:
                        pass

            # appending to the resulting list
            tilelist.append(Tile(cfg))

        return tilelist
