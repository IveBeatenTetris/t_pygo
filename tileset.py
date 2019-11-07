# dependencies
from .utils import (
    PATH,
    draw,
    getFrames,
    loadAssets,
    prettyPrint
)
import pygame as pg

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
                "name": "NoNameTile",
                "image": each,
                "id": i,
                "block": False,
            }
            # additional tile properties
            for props in self.config["tiles"]:
                if props["id"] == i:
                    for property in props["properties"]:
                        cfg[property["name"]] = property["value"]
            # appending to the resulting list
            tilelist.append(Tile(cfg))
        return tilelist
class Tile(pg.sprite.Sprite):
	"""cut out a sprite from an image. actually its just replacement."""
	default = {
		"name": "NoName",
		"block": False,
		"visible": True
	}
	def __init__(self, config={}):
		"""."""
		pg.sprite.Sprite.__init__(self)

		self.image = config["image"]# pygame surface
		self.rect = self.image.get_rect()# pygame rect
		self.id = config["id"]# int

		# additional attributes
		try:
		    self.name = config["name"]# str
		except KeyError:
		    self.name = self.default["name"]
		try:
		    self.block = config["block"]# bool
		except KeyError:
		    self.block = self.default["block"]
		try:
		    self.visible = config["visible"]# bool
		except KeyError:
		    self.visible = self.default["visible"]
