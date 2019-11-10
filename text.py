from .utils import (
	validateDict,
    draw
)
import pygame as pg

class Text(pg.sprite.Sprite):
	"""text surface. ready to be drawn."""
	default = {
		"font": "Verdana",
		"fontsize": 16,
		"color": (0, 0, 0),
		"text": "No Text",
		"antialias": True
	}
	def __init__(self, config={}):
		"""
		creates a text that can be drawn to any surface.
		first validates the config dict by camparing it with its default values.
		validateDict() is going to do that for you.
		'fontsize' its in the name.
		'color' should be tuple by 3 like (50, 110, 95).
		'text' only one-liners right now.
		'antialias' if 'false' the font will appear pixelated.
		'font' creates a new pygame.font from an installed system font.
		"""
		self.config = validateDict(config, self.default)# dict
		pg.sprite.Sprite.__init__(self)
		pg.font.init()

		self.fontsize = self.config["fontsize"]# int
		self.color = self.config["color"]# tuple
		self.text = self.config["text"]# str
		self.antialias = self.config["antialias"]# bool
		self.font = pg.font.SysFont(# pygame.font
			self.config["font"],
			self.fontsize
		)

		self.__create()
	def __create(self):
		"""
		recreate the image-surface of the text. this is necessary since the
		pygame.font only creates images instead of an interactive
		text-objective.
		"""
		self.image = self.font.render(self.text, self.antialias, self.color)
	def update(self, cfg):
		"""updates attributes with the given parameters. 'cfg' must be dict."""
		try:
			self.text = cfg["text"]
		except KeyError:
			pass

		self.__create()
