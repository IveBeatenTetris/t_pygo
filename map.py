from .utils import (
    PATH,
    loadAssets,
    draw,
    createTiledMap,
    getFrames
)
import pygame as pg

class Map(pg.Surface):
    """
    holds tilesets, tiles and layers. the map object itself can be drawn on a
    surface for preview purpose. for real map drawing us the layers of the map.
    example:
    for layer in self.layers:
        draw(self.layers[layer], surface)
    or:
        draw(self.layers, surface)
    """
    def __init__(self, name):
        """
        load a dict from a json-file and make it config.
        'name' is gonna be adapted when the map is created with 'tiled'.
        'size' recalculated map size. consider using the rect anyways.
        'tilesize' most commonly its 16x16 or 32x32.
        'tiles' is a list of all the tiles cut out from the image.
        'layers' every tile is drawn to its layer. you can draw each layer
            sperately or use the entiry layers-dict to draw on a surface.
        'blocks' is a list with all non-passable tiles.
        """
        # combine path + name to get the asset by its tail
        for each in loadAssets(PATH["maps"] + "\\" + name):
            if each["type"] == "map":
                self.config = each# dict
        # additional attributes
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
        self.blocks = []# list
        for _, layer in self.layers.items():
            if layer.type == "tilelayer":
                # getting playerstart from a layer. may only be placed once per
                # map
                if layer.player_start:
                    self.playerstart = layer.player_start# pygame.rect
                # filling self.blocks with all layers blocks
                for each in layer.blocks:
                    self.blocks.append(each)
        # initiating surface
        pg.Surface.__init__(self, self.size, pg.SRCALPHA)
        self.rect = self.get_rect()# pygame.rect
        # drawing the preview map
        self.preview = self.__mix()# pygame.surface
    def __createLayers(self):# dict
        """
        return a dict of layers. each is an own dict with several attributes.
        also appending a list of tiles for that layer as well as their
        tile-sizes.
        """
        layers = {}

        for each in self.config["layers"]:
            # tiled layer (proof that this dict comes from a 'tiled'-file.)
            if each["type"] == "tilelayer":
                # updating layers
                each.update({
                    "tiles": self.tiles,
                    "tilesize": self.tilesize
                })
                layer = Layer(each)
                layers.update({each["name"]: layer})
            # layer group
            elif each["type"] == "group":
                pass
            # object layer
            elif each["type"] == "objectgroup":
                # updating layers
                layer = Layer(each)
                layers.update({each["name"]: layer})

        return layers
    def __createTilesets(self):# dict
        """create a dict of tilesets and return it."""
        tilesets = {}
        # for each tileset-config
        for cfg in self.config["tilesets"]:
            split = cfg["source"].split("/")
            name = split[-2]
            file = split[-1]
            # updating the list
            tilesets.update({name: Tileset(name)})
        return tilesets
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
    # experimental
    def __mix(self):# pygame.surface
        """
        merge some layers for better fps performance on higher resolutions.
        for now it renders every layer without exception.
        """
        surface = pg.Surface(self.rect.size)

        for layer in self.layers:
            if self.layers[layer].type == "tilelayer":
                draw(self.layers[layer], surface)

        return surface
class Layer(pg.Surface):
    """
    representation of a 'tiled'-layer. each layer can be drawn seperately. it
    holds information about all its used tiles, its names, blocks, invisibles
    etc.
    can also be a 'object' layer for placing events and so on.
    """
    def __init__(self, config):
        """
        'type' declares the layer type for comparison.
        'name' declares the layer name for comparison.
        'tilelayer':
            'config' becomes the returned value of 'createTiledMap()'. in this
            case a dict.
            'size' recalculated map size. consider using the rect anyways.
            'blocks' all non-passable tiles on this layer.
            'player_start' this is where the player starts when placed in
            'tiled'.
        'objectgroup':
            'config' now becomes a config dict of an object layer from a tiled
            file.
        """
        self.type = config["type"]# str
        self.name = config["name"]# str
        # tile layer
        if self.type == "tilelayer":
            self.config = createTiledMap(config, config["tiles"])# dict
            # additional attributes
            self.size = (# tuple
                config["width"] * config["tilesize"][0],
                config["height"] * config["tilesize"][1]
            )
            self.image = self.config["image"]# pygame.surface
            self.blocks = self.config["blocks"]# list
            self.player_start = self.config["player_start"]# pygame rect / none
            # drawing to surface
            pg.Surface.__init__(self, self.size, pg.SRCALPHA)
            draw(self.image, self)
        # object layer
        # object layer
        elif self.type == "objectgroup":
            self.config = config# dict
            # additional attributes
            self.objects = self.__createObjects()# list
    def __createObjects(self):
        """from a config dict of a 'tiled'-map create interactive objects."""
        objects = []

        for obj in self.config["objects"]:
            # create an event area drawn in 'tiled'
            if obj["type"] == "event":
                pass

        return objects
class Tileset(pg.Surface):
    """spritesheet object. can be drawn to a surface for preview purpose."""
    def __init__(self, name):
        """
        opens a tileset by the given name. the opened file is JSON-file that
        holds all information for initiating this tileset object.
        'name' comes from the json-file.
        'path' actually path to the holding directory. this one is been
            appended through opening the tileset as an asset like in
            'loadAssets(path + name)'.
        'tilesize' most commonly its 16x16 or 32x32.
        'tiles' is a list of all the tiles cut out from the image.
        """
        # combining path and name to open assets from that path
        for each in loadAssets(PATH["tilesets"] + "\\" + name):
            if each["type"] == "tileset":
                self.config = each# dict
        # additional attributes
        self.name = self.config["name"]# str
        self.path = self.config["filepath"]# str
        self.image = pg.image.load(# pygame.surface
            self.path + "\\" + self.config["image"]
        )
        self.tilesize = (# tuple
            self.config["tilewidth"],
            self.config["tileheight"]
        )
        self.tiles = self.__createTiles()# list
        # display related stuff
        pg.Surface.__init__(self, self.image.get_rect().size, pg.SRCALPHA)
        draw(self.image, self)
    def __createTiles(self):# list
        """
        return a list of all tiles in the given tileset-image.
        'cfg' will hold additional properties. these will be added to a
        config-dict that is used to create a tile object.
        """
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
	"""cut out a sprite from an image. actually its just displacement though."""
	default = {
		"name": "No Name",
		"block": False,
		"visible": True
	}
	def __init__(self, config={}):
		"""
        'id' is been generated by enumerating the whole image. starting with 0.
        'name' is depending on if there is a given name for the tile in the
            json-config file. else its called 'noname'.
        'block' is an argument to check if an entity is able to move pass this
            tile.
        'visible' determines if the tile is going to be rendered or not.
        """
		pg.sprite.Sprite.__init__(self)
        # additional attributes
		self.image = config["image"]# pygame.surface
		self.rect = self.image.get_rect()# pygame.rect
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
