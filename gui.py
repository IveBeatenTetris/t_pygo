from .utils import (
    PATH,
    LIBPATH,
    draw,
    validateDict,
    loadAssets,
    getAnchors,
    wrapText,
    drawBorder,
    convertRect,
    scale
)
from .camera import Camera
import pygame as pg

# overall functions
def convertElement(cfg, parent):
    """
    using this function to convert a interface element from a json file into a
        valid interface element object. returns the valid interface element.
    'cfg' needs to be a converted dict from json file.
    'parent' must be pygame.rect.
    """
    element = None
    # resetting properties with each loop
    c = {
        "type": None,
        "name": "Unnamed",
        "rect": pg.Rect(0, 0, 0, 0),
        "background": None
    }
    # overwriting properties
    for name, prop in cfg.items():
        c[name] = prop
    # additional properties
    if "rect" in cfg:
        # since we suport percentage and positional strings in
        # rect-lists we need to calculate a new rect with valid
        # values for drawing
        c["rect"] = convertRect(cfg["rect"], parent)
    if "background" in cfg:
        c["background"] = tuple(cfg["background"])
    # appending gui element objects to 'elements' list
    if "type" in cfg:
        # menus
        if cfg["type"] == "dropdown":
            element = DropDownMenu(c)
        # elements
        elif cfg["type"] == "menubar":
            element = MenuBar(c)
        elif cfg["type"] == "infobar":
            element = InfoBar(c)
        elif cfg["type"] == "panel":
            element = Panel(c)
        elif cfg["type"] == "button":
            element = Button(c)

    return element

class GuiMaster(pg.Surface):
    """
    master element for many gui elements to inherit from. comes with diverse
    events ans additional properties for surfaces.
    """
    default = {
        "name": "Unnamed Element",
        "rect": pg.Rect(0, 0, 200, 25),
        "background": (10, 10, 10)
    }
    def __init__(self, config={}):
        """
        'name' name of the element as str.
        'parent' rect of the bigger surface for calculating positional
            properties.
        'background' can be tuple of 3 ints or none. if 'none' then render the
            background transparent.
        'anchors' anchorpoints for positional arguments.
        """
        # creating a new dict based on comparison of two
        self.config = validateDict(config, self.default)# dict
        self.name = self.config["name"]# str
        # declaring parent for positional properties
        self.parent = pg.display.get_surface().get_rect()# pygame.rect
        self.background = self.config["background"]# none / tuple
        self.rect = self.config["rect"]# pygame.rect
        self.anchors = getAnchors(self.rect.size)# dict
        # building surface
        self.build()
    def build(self):
        """rebuilding everything."""
        # initiating surface
        pg.Surface.__init__(self, self.rect.size, pg.SRCALPHA)
        # updating anchors
        self.anchors = getAnchors(self.rect.size)
        # drawing
        draw(self.background, self)
    def update(self):
        """
        run this method with each main loop. can be overwritten by the calling
            element.
        """
        pass
class Interface(pg.Surface):
    """
    acts like a big surface to stat drawing the element tree from a json-file.
    """
    def __init__(self, name):
        """
        draws its size from the running window.
        'elements' a list of all gui elements in the correct drawing order.
        'menus' a list of all accessable menus of the interface ready to be
            called.
        """
        # combine path + name to get the asset by its tail
        for js in loadAssets(PATH["interface"] + "\\" + name):# dict
            if js["type"] == "interface":
                self.config = js
        # taking rect from pygame.display
        self.rect = pg.display.get_surface().get_rect()# pygame.rect
        self.elements = []# list
        self.menus = []# list
        # building surface / drawing
        self.__build()
    def __build(self):
        """
        building interface structure from file description. filling
            'self.elements' and 'self.menus' with gui elements.
        """
        # filling 'self.elements' later with real element objects
        self.elements = []# list
        self.menus = []# list
        # initiating surface
        pg.Surface.__init__(self, self.rect.size, pg.SRCALPHA)
        # creating menus
        if "menus" in self.config:
            for menu, prop in self.config["menus"].items():
                prop.update({"name": menu})
                self.menus.append(convertElement(prop, self.rect))
        # creating visible gui elements
        if "elements" in self.config:
            for elem in self.config["elements"]:
                self.elements.append(convertElement(elem, self.rect))
        # drawing each element to interface
        for e in self.elements:
            draw(e, self, e.rect)
        # drawing menu if activated
        for m in self.menus:
            pass
    def draw(self, object, position=(0, 0)):
        """drawing something to the interface."""
        draw(object, self, position)
    def resize(self, size):
        """
        set a new size for interface. needs to be rebuilt.
        'size' needs to be tuple.
        """
        self.rect.size = size
        # rebuilding
        self.__build()
    def update(self):
        """run this method with each main loop."""
        for e in self.elements:
            # updating each element
            e.update()
            # drawing elements to interface
            # reduced drawing functionallity to 'menubar' and 'infobar' for a
            # better fps performance
            if type(e) is MenuBar or type(e) is InfoBar:
                draw(e, self, e.rect)

class Button(GuiMaster):
    """interactive gui element."""
    cfg = {
        "text": "Button",
        "color": (200, 200, 200),
        "fontsize": 16,
        "bold": False,
        "italic": False,
        "antialias": True,
        "hover": (20, 20, 20)
    }
    def __init__(self, config={}):
        """
        'text' gui text object. ready to be drawn.
        'hover' different color tuple for highlighting on 'hover' event.
        'state' state of activation. 'true' on click.
        """
        # inherit from gui master
        GuiMaster.__init__(self, config)
        # updating 'config' with properties from json file
        for k, v in config.items():
            self.cfg[k] = v
        # assigning attributes
        self.text = Text({# text object
            "text": self.cfg["text"],
            "fontsize": self.cfg["fontsize"],
            "bold": self.cfg["bold"],
            "italic": self.cfg["italic"],
            "color": self.cfg["color"]
        })
        self.state = False# bool
        self.hover = tuple(self.cfg["hover"])# tuple
        # building / drawing to surface
        self.build()
        # drawing text in the very center of the button
        draw(
            self.text,
            self,
            (
                self.anchors["midcenter"][0] - int(self.text.rect.width / 2),
                self.anchors["midcenter"][1] - int(self.text.rect.height / 2)
            )
        )
    def update(self):
        """run this method with each main loop."""
        # determining background
        if self.rect.collidepoint(pg.mouse.get_pos()):
            bg = self.hover
        else:
            bg = self.background
        # drawing background
        draw(bg, self)
        # drawing text in the very center of the button
        draw(
            self.text,
            self,
            (
                self.anchors["midcenter"][0] - int(self.text.rect.width / 2),
                self.anchors["midcenter"][1] - int(self.text.rect.height / 2)
            )
        )
    def mouseOver(self, events):
        """return 'true' if the mouse hovers the button."""
        mouse = pg.mouse.get_pos()
        hover = False

        for event in events:
            if self.rect.collidepoint(mouse):
                hover = True

        # rebuilding the surface so the hover effect can pop in
        self.build()

        return hover
    def leftClick(self, events):
        """returns 'true' if button is left-clicked."""
        mouse = pg.mouse.get_pos()
        click = False

        for event in events:
            if self.mouseOver(events):
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    click = True

        return click
class DropDownMenu(GuiMaster):
    """a drop down menu. draw this on a button call."""
    def __init__(self, config={}):
        """."""
        # inherit from gui master
        GuiMaster.__init__(self, config)
class InfoBar(GuiMaster):
    """used for displaying information in a small bar."""
    def __init__(self, config={}):
        """."""
        # inherit from gui master
        GuiMaster.__init__(self, config)
class MenuBar(GuiMaster):
    """a menu bar to draw pull down menus from."""
    def __init__(self, config={}):
        """
        'elements' a list of gui element objects to draw.
        """
        # inherit from gui master
        GuiMaster.__init__(self, config)
        # filling self.elements with real element objects
        self.elements = []# list
        if "elements" in config:
            for elem in config["elements"]:
                self.elements.append(convertElement(elem, self.rect))
        # rebuild surface
        self.update()
    def update(self):
        """run this method with each main loop."""
        for elem in self.elements:
            # updating each element
            if type(elem) is Button:
                elem.update()
            # drawing each element
            draw(elem, self, elem.rect)
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
class Panel(GuiMaster):
    """displays a panel in the interface."""
    def __init__(self, config={}):
        """."""
        # inherit from gui master
        GuiMaster.__init__(self, config)
class Text(pg.sprite.Sprite):
    """text surface. ready to be drawn."""
    default = {
    	"font": "ebrima",
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
        pygame. font only creates images instead of interactive text-objects.
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
            self.image = self.font.render(
                self.text,
                self.antialias,
                self.color
            )
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
