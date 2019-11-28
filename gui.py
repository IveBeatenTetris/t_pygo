from .utils import (
    PATH,
    LIBPATH,
    draw,
    validateDict,
    loadAssets,
    getAnchors,
    wrapText,
    drawBorder,
    scale
)
from .camera import Camera
import pygame as pg

class Button(pg.sprite.Sprite):
    """interactive gui element."""
    default = {
        "size": (120, 40),
        "background": (0, 0, 0),
        "hoverbackground": (20, 20, 20),
        "text": "Button",
        "textcolor": (255, 255, 255),
        "fontsize": 16,
        "bold": False,
        "italic": False,
        "position": (0, 0)
    }
    def __init__(self, config={}):
        """
        'anchors' holds shortcuts for positional arguments like "midcenter" or
            "topright" etc for documentation look into 'utils.py'.
        'text' the actual displayed text.
        """
        # comparing dicts and creating a new one
        self.config = validateDict(config, self.default)# dict
        # initiating sprite
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface(self.config["size"])# pygame.surface
        # additional attributes
        self.rect = self.image.get_rect()# pygame.rect
        self.rect.topleft = self.config["position"]# tuple
        self.anchors = getAnchors(self.rect.size)# dict
        self.text = Text({# text object
            "text": self.config["text"],
            "fontsize": self.config["fontsize"],
            "bold": self.config["bold"],
            "italic": self.config["italic"],
            "color": self.config["textcolor"]
        })
        # building the sprite object
        self.__build()
    def __build(self):
        """redrawing everything"""
        # determining background
        if self.rect.collidepoint(pg.mouse.get_pos()):
            bg = self.config["hoverbackground"]
        else:
            bg = self.config["background"]
        # drawing on button
        draw(bg, self.image)
        # drawing text in the very center of the button
        draw(
            self.text,
            self.image,
            (
                self.anchors["midcenter"][0] - int(self.text.rect.width / 2),
                self.anchors["midcenter"][1] - int(self.text.rect.height / 2)
            )
        )
    def hover(self, events):
        """return 'true' if the mouse hovers the button."""
        mouse = pg.mouse.get_pos()
        hover = False

        for event in events:
            if self.rect.collidepoint(mouse):
                hover = True

        # rebuilding the surface so the hover effect can pop in
        self.__build()

        return hover
    def leftClick(self, events):
        """returns 'true' if button is left-clicked."""
        mouse = pg.mouse.get_pos()
        click = False

        for event in events:
            if self.hover(events):
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    click = True

        return click
class MiniMap(pg.Surface):
    """display a miniature version of an area around the players position."""
    default = {
        "map": None,
        "size": (100, 75)
    }
    def __init__(self, config={}):
        """."""
        # comparing dicts and creating a new one
        self.config = validateDict(config, self.default)# dict
        # initiating surface
        pg.Surface.__init__(self, self.config["size"])
        # determining map image
        if self.config["map"]:# pygame.surface
            img = self.config["map"].preview
        else:
            img = pg.image.load(LIBPATH["noimage"])
        self.image = img
        self.rect = pg.Rect((0, 0), self.config["size"])# pygame.rect
        #draw(self.image, self)
        draw((0, 0, 0), self)
    def update(self, screenshot):
        """updates this class with each game loop."""
        # if not none
        if screenshot:
            # scaling screenshot
            img = scale(
                screenshot,
                (
                    int(screenshot.get_rect().width / 3),
                    int(screenshot.get_rect().height / 3)
                )
            )
            #draw((0, 0, 0), self)
            draw(img, self, "center")
class Overlay(pg.Surface):
    """
    for dimmed backgrounds on menus. 'opacity' somehow works backwards. means
    that 0 is for none blending while 255 is for full rendering.
    """
    default = {
        "background": (0, 0, 0),
        "size": (320, 240),
        "opacity": 255
    }
    def __init__(self, config={}):
        """constructor"""
        # comparing dicts and creating a new one
        self.config = validateDict(config, self.default)# dict
        # initiating surface
        pg.Surface.__init__(self, self.config["size"])
        # setting opacity if there is one
        self.set_alpha(self.config["opacity"])
class Text(pg.sprite.Sprite):
    """text surface. ready to be drawn."""
    default = {
    	"font": "Verdana",
    	"fontsize": 16,
    	"color": (0, 0, 0),
    	"text": "No Text",
    	"antialias": True,
    	"bold": False,
    	"italic": False,
        "size": (100, 100),
        "wrap": False
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
        'wrap' if 'true' then call a function to wrap the text into a given
            rect.
        'size' tuple of 2 ints. only for reference purpose.
        """
        # comparing both dicts and creating a new one from it
        self.config = validateDict(config, self.default)# dict
        # initiating
        pg.sprite.Sprite.__init__(self)
        pg.font.init()
        # additional attributes
        self.fontsize = self.config["fontsize"]# int
        self.color = self.config["color"]# tuple
        self.text = self.config["text"]# str
        self.antialias = self.config["antialias"]# bool
        self.font = pg.font.SysFont(# pygame.font
        	self.config["font"],
        	self.fontsize
        )
        self.font.set_bold(self.config["bold"])
        self.font.set_italic(self.config["italic"])
        self.wrap = self.config["wrap"]# bool
        self.size = self.config["size"]# tuple
        # image and rect are going to be created there
        self.__create()
    def __create(self):
        """
        recreate the image-surface of the text. this is necessary since the
        pygame.font only creates images instead of interactive text-objects.
        usually the text-object doesnt have to be recreated anyways.
        """
        if self.wrap:
            self.image = wrapText(
                self.text,
                self.color,
                pg.Rect((0, 0), self.size),
                self.font,
                aa = self.antialias
            )
        else:
            self.image = self.font.render(self.text, self.antialias, self.color)
        self.rect = self.image.get_rect()
    def update(self, cfg={}):
    	"""
        updates attributes with the given parameters. 'cfg' must be dict.
        recreates text surface at the end.
        """
    	try:
    		self.text = str(cfg["text"])
    	except KeyError:
    		pass

    	self.__create()
class TextBox(pg.Surface):
    """surface for displaying text."""
    default = {
        "text": "Default Text",
        "type": "textbox",
        "font": "verdana",
        "fontsize": 16,
        "size": (300, 100),
        "position": (0, 0),
        "bold": False,
        "italic": False,
        "wrap": True,
        "color": (255, 255, 255),
        "background": (0, 0, 0),
        "padding": None
    }
    def __init__(self, config={}):
        """
        'type' declares if the object is gonna be build as 'textbox' or
            'speechbubble'
        'call' bool to check if the textbox is called or not.
        'padding' text padding from the corners of the textbox rect.
        'text' holds a whole text object with warpped or non-wrapped text.
        """
        # creating a new dict based on comparison of two
        self.config = validateDict(config, self.default)# dict
        self.type = self.config["type"]# str
        self.call = False# bool
        pg.Surface.__init__(self, self.config["size"], pg.SRCALPHA)
        self.rect = self.get_rect()# pygame.rect
        self.rect.topleft = self.config["position"]
        # additional attributes
        self.padding = self.config["padding"]# none / int
        self.text = Text({# text object
            "text": "Neque porro quisquam est qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit... 'There is no one who loves pain itself, who seeks after it and wants to have it, simply because it is pain...'",
            "fontsize": self.config["fontsize"],
            "font": self.config["font"],
            "bold": self.config["bold"],
            "italic": self.config["italic"],
            "color": self.config["color"],
            "size": self.calculateRect(self.rect).size,
            "wrap": self.config["wrap"]
        })
        self.__build()
    def __build(self):
        """composing surface."""
        # drawing background
        draw(self.config["background"], self)
        # drawing text depending on margins
        if self.padding:
            if type(self.padding) is int:
                pos = (self.padding, self.padding)
            elif type(self.padding) is list or type(self.padding) is list:
                pos = self.padding
        else:
            pos = (0, 0)
        draw(self.text, self, pos)
    def calculateRect(self, rect):
        """recalculating rect size based on padding and margin"""
        p = self.padding

        if p:
            if type(p) is int:
                rect.width = rect.width - (p * 2)
                #rect.height = rect.height - (p * 2)

        return rect
    def setPosition(self, pos):
        """updating rect position."""
        self.rect.topleft = pos
class Interface(pg.Surface):
    """surface for displaying multiple gui panels."""
    def __init__(self, name, size=(320, 240)):
        """
        generates multiple gui panels and drawing them to its surface.
        'config' dict from json-file with additional properties.
        'name' name of the panel.
        'panels' a dict of panel objects ready to been drawn to screen.
        """
        # combine path + name to get the asset by its tail
        for each in loadAssets(PATH["interface"] + "\\" + name):# dict
            if each["type"] == "interface":
                self.config = each
        self.name = self.config["name"]# str
        self.path = self.config["filepath"]# str
        self.image = pg.image.load(# pygame.surface
            self.path + "\\" + self.config["image"]
        )
        # initiating surface
        pg.Surface.__init__(self, size, pg.SRCALPHA)
        self.rect = self.get_rect()# pygame.rect
        self.panels = self.__createPanels()# dict
        # drawing panels to interface
        self.__build()
    def __build(self):
        """building panels."""
        for name, panel in self.panels.items():
            pg.Surface.__init__(self, self.rect.size, pg.SRCALPHA)
            draw(panel, self, panel.rect)
    def __createPanels(self):
        """creating panels and append them to a returning dict."""
        panels = {}

        if "panels" in self.config:
            p = self.config["panels"]
            if "money" in p:
                p["money"].update({
                    "name": "money",
                    "image": self.image
                })
                panels.update({"money": MoneyPanel(p["money"])})

        return panels
    def update(self):
        """calling this method with each game loop."""
        # rebuilding panel
        self.__build()
# interface panels
class MoneyPanel(pg.Surface):
    """displays money in the interface."""
    default = {
        "rect": [0, 0, 0, 0],
        "imagerect": [0, 0, 0, 0],
        "image": pg.image.load(LIBPATH["noimage"]),
        "background": None
    }
    def __init__(self, config={}):
        """
        this panel acts as a surface ready to been drawn to another surface.
        'imagerect' needed to draw the correct position of the icon set to the
            icon.
        'icon' surface for drawing the icon surface.
        """
        # creating a new dict based on comparison of two
        self.config = validateDict(config, self.default)# dict
        self.rect = pg.Rect(self.config["rect"])# pygame.rect
        self.imagerect = pg.Rect(self.config["imagerect"])# pygame.rect
        self.image = self.config["image"]# pygame.surface
        self.icon = pg.Surface(self.imagerect.size, pg.SRCALPHA)# pygame.surface
        self.background = self.config["background"]# none / tuple
        # initiating surface
        pg.Surface.__init__(self, self.rect.size, pg.SRCALPHA)
        self.__build()
    def __build(self):
        """building the surface object."""
        if self.background:
            # filling surface
            draw(tuple(self.background), self)
        else:
            # reinitiating surface
            pg.Surface.__init__(self, self.rect.size, pg.SRCALPHA)
        # drawing on icon
        draw(self.image, self.icon, self.imagerect)
        # drawing icon to panel
        draw(self.icon, self)
    def draw(self, object, position=(0, 0)):
        """drawing something to the panel."""
        self.__build()
        draw(object, self, position)
