from .utils import (
    PATH,
    loadJSON,
    draw,
    createTiledMap
    )
from .tileset import Tileset
import pygame as pg

class Map(pg.Surface):
    """
    holds tilesets, tiles and layers. the map object itself can be drawn on a
    surface for preview purpose. for real map drawing us the layers of the map.
    example:
    for layer in self.layers:
        draw(self.layers[layer], surface)
    """
    def __init__(self, path):
        """."""
        self.config = loadJSON(path)# dict
        self.name = self.config["name"]# str
        self.size = (# tuple
            self.config["width"] * self.config["tilewidth"],
            self.config["height"] * self.config["tileheight"]
        )
        self.tilesize = (# tuple
            self.config["tilewidth"],
            self.config["tileheight"]
        )
        self.tilesets = self.__createTilesets()# dict
        self.tiles = self.__getTiles()# list
        self.layers = self.__createLayers()# dict

        pg.Surface.__init__(self, self.size, pg.SRCALPHA)
        # drawing the preview to the map-surface
        self.__previewMap()
    def __getTiles(self):# list
        """
        get tile objects from every appended tileset and return them in one
        single list. means: multiple tilesets = more tiles
        """
        tiles = []

        for k, v in self.tilesets.items():
            for tile in v.tiles:
                tiles.append(tile)

        return tiles
    def __createTilesets(self):# dict
        """reate a dict of tilesets and return it."""
        tilesets = {}

        for cfg in self.config["tilesets"]:
            split = cfg["source"].split("/")
            name = split[-2]
            file = split[-1]
            # getting an tsx-file but we need a json
            path = (
                PATH["tilesets"] +
                "\\" +
                name +
                "\\" +
                file.split(".")[0] +
                ".json"
            )
            #config = loadJSON(path)
            tilesets.update({name: Tileset(path)})

        return tilesets
    def __createLayers(self):# dict
        """
        return a dict of layers. each is an own dict with several
        attributes.
        """
        layers = {}

        for each in self.config["layers"]:
            # tiled layer
            if each["type"] == "tilelayer":
                # updating layers
                each.update({
                    "tiles": self.tiles,
                    "tilesize": self.tilesize
                    })
                layer = Layer(each)
                layers.update({each["name"]: layer})

            # group layer
            elif each["type"] == "group":
                pass

        return layers
    def __previewMap(self):# pygame Surface
        """."""
        for layer in self.layers:
            draw(self.layers[layer], self)
class Layer(pg.Surface):
    """."""
    def __init__(self, config):
        """."""
        self.name = config["name"]# str
        self.size = (# tuple
            config["width"] * config["tilesize"][0],
            config["height"] * config["tilesize"][1]
        )
        pg.Surface.__init__(self, self.size, pg.SRCALPHA)

        tmap = createTiledMap(config, config["tiles"])
        draw(tmap["image"], self)
