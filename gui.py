from .utils import (
    PATH,
    LIBPATH,
    FONTS,
    draw,
    validateDict,
    loadAssets,
    getAnchors,
    wrapText,
    drawBorder,
    convertRect,
    getDisplay,
    repeatBG,
    scale
)
from .camera import Camera
from .controller import Controller
import pygame as pg
import sys, os

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
        if cfg["type"] == "menu":
            element = Menu(c)
        # elements
        if cfg["type"] == "menubar":
            element = MenuBar(c)
        elif cfg["type"] == "infobar":
            element = InfoBar(c)
        elif cfg["type"] == "panel":
            element = Panel(c)
        elif cfg["type"] == "button":
            element = Button(c)
        elif cfg["type"] == "text":
            element = Text(c)

    return element

class App:
    """pygames window module with extended features."""
    default = {
        "size": (320, 240),
        "title": "No Title",
        "resizable": False,
        "fullscreen": False,
        "background": LIBPATH["windowbg"],
        "backgroundrepeat": None,
        "icon": LIBPATH["windowicon"],
        "fps": 30
    }
    def __init__(self, config={}):
        """
        initiates pygame to act as a pygame-window.
        'size' window size in a tuple for short reference only.
        'title' is gonna be displayed as the windows title.
        'icon' is displayed next to the title in the window.
        'preffered_fps' - its in the name.
        'fps' is gonna be updated from the windows update-method.
        'paused' is a switch for showing a gui and closing it. handled by
            'self.pause()'.
        'mode' is for switching trough modes like 'moving' or 'paused'.
        'controller' decided to put it into the window. its been updated in the
        'window.events()'-method.
        'display' holds the actual pygame window.
        'screenshot' this surface can be used to simulate frozen screens like
            in menus. its refreshed by calling 'self.screenShot()'
        'anchors' is used for quick-pointing a part of the rect. for example:
            draw(object, self, self.anchors["midcenter"]).
        'fullscreen' if 'true' it renders the window maximized and borderless.
        'background' used to draw to background. might be 'str' or 'tuple'. if
            'string' then use it as image path and load a pygame.image surface.
        'bgrepeat' str with either 'x' 'y' or 'xy'.
        '_events' with each game-loop this list will become the new
            pygame.events.
        """
        # centering window
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        # initiate pygame
        pg.init()
        # creating a dict based of comparison of config{} and default{}
        self.config = validateDict(config, self.default)# dict
        # additional attributes
        self.size = self.config["size"]# tuple
        self.title = self.config["title"]# str
        self.icon = self.config["icon"]# str / pygame.surface
        self.clock = pg.time.Clock()# pygame.clock
        self.preffered_fps = self.config["fps"]# int
        self.fps = 0# int
        self.paused = False# bool
        self.mode = "moving"# str
        self.controller = Controller()# controller (pygame.joystick.joystick)
        # display related stuff
        self.display = getDisplay(# pygame.surface
            self.config["size"],
            resizable = self.config["resizable"]
        )
        self.screenshot = None# none / pygame.surface
        self.changeTitle(self.config["title"])
        self.changeIcon(self.icon)
        self.anchors = getAnchors(self.size)# dict
        # background related
        self.fullscreen = self.config["fullscreen"]# bool
        self.bgrepeat = self.config["backgroundrepeat"]# str
        self.background = self.__createBackground(# pygame.surface
            self.config["background"]
        )
        # event related
        self._events = []# list
    # game routines
    def update(self):
        """updates stuff at apps loop-end."""
        pg.display.update()
        self.clock.tick(self.preffered_fps)
        self.fps = int(self.clock.get_fps())
    def quit(self):
        """exits the app."""
        pg.quit()
        sys.exit()
    def pause(self):
        """pauses the game or continues it."""
        if self.paused is True:
            self.paused = False
        else:
            self.paused = True
            # create a screenshot
            self.screenshot = self.display.copy()
    # display stuff
    def __createBackground(self, bg):
        """creates background based on background properties."""
        # declaring background type
        if type(bg) is str:
            bg = pg.image.load(bg)
        elif type(bg) is tuple:
            pass
        # checking background repeat
        if type(bg) is pg.Surface:
            if self.config["backgroundrepeat"]:
                bg = repeatBG(
                    bg,
                    self.size,
                    self.bgrepeat
                )

        return bg
    def draw(self, object, position=(0, 0)):
        """draw everything to the windows surface."""
        draw(object, self.display, position)
    def resize(self, size=None):
        """
        'size' needs to be a tuple. if no 'size' then return if the window has
            been resized in a bool.
        """
        if size:
            self.display = getDisplay(# pygame.surface
                size,
                resizable = self.config["resizable"],
                fullscreen = self.fullscreen
            )
            self.draw(self.background)
            self.size = size
            self.anchors = getAnchors(self.size)
        else:
            resized = False
            for e in self._events:
                if e.type is pg.VIDEORESIZE:
                    resized = True

            return resized
    def screenShot(self, surface=None):
        """creates a copy of the all displayed things and save it."""
        if surface:
            self.screenshot = surface.copy()
        else:
            self.screenshot = self.display.copy()
    # event related methodes
    def events(self):# pygame.event
        """pygame events. updates the controller with events."""
        events = []
        keys = self.pressedKeys()
        # keyboard and mouse events
        for event in pg.event.get():
            # quit application
            if event.type is pg.QUIT:
                self.quit()
            if keys[pg.K_LALT] and keys[pg.K_F4]:
                self.quit()
            # resizing the window
            if event.type is pg.VIDEORESIZE:
                self.resize(event.size)
            # going fullscreen
            if event.type is pg.KEYDOWN and event.key is pg.K_F12:
                pass
            # finalizing event list
            events.append(event)
        # applying these events to the window-event list
        self._events = events
        # updating controller element if there is one
        if self.controller.joystick:
            self.controller.update(events)

        return events
    def pressedKeys(self):
        """return pygame-event's pressed-keys."""
        return pg.key.get_pressed()
    def keys(self):
        """might look for a more efficient way to check for hitten keys."""
        keys = {
            "return": False,
            "esc": False,
            "alt": False,
            "e": False,
            "f1": False,
            "f4": False
        }

        for event in self._events:
            if event.type is pg.KEYDOWN and event.key == pg.K_RETURN:
                keys["return"] = True
            if event.type is pg.KEYDOWN and event.key == pg.K_ESCAPE:
                keys["esc"] = True
            if event.type is pg.KEYDOWN and event.key == pg.K_LALT:
                keys["alt"] = True
            if event.type is pg.KEYDOWN and event.key == pg.K_F1:
                keys["f1"] = True
            if event.type is pg.KEYDOWN and event.key == pg.K_F4:
                keys["f4"] = True
            if event.type is pg.KEYDOWN and event.key == pg.K_e:
                keys["e"] = True

        return keys
    def mouseWheel(self):
        """mouse wheel event checking. returns a string."""
        wheel = "none"

        for event in self._events:
            if event.type is pg.MOUSEBUTTONDOWN and event.button == 4:
                wheel = "up"
            elif event.type is pg.MOUSEBUTTONDOWN and event.button == 5:
                wheel = "down"

        return wheel
    # window appearance
    def changeIcon(self, path):
        """create an icon for the window from an image."""
        if type(path) is pg.Surface:
            icon = path
        elif type(path) is str:
            icon = pg.image.load(path)

        icon = pg.transform.scale(icon, (32, 32))
        pg.display.set_icon(icon)
    def changeTitle(self, title):
        """change the window-title. 'title' should be a string."""
        if type(title) is not str:
            title = str(title)
        pg.display.set_caption(title)
class GuiMaster(pg.Surface):
    """
    master-element for many gui elements to inherit from. comes with diverse
    events ans additional properties for surfaces.
    """
    default = {
        "name": "Unnamed Element",
        "rect": pg.Rect(0, 0, 200, 25),
        "background": None
    }
    def __init__(self, config={}):
        """
        'name' name of the element as str.
        'parent' rect of the bigger surface for calculating positional
            properties.
        'background' can be tuple of 3 ints or none. if 'none' then render the
            background transparent.
        'anchors' anchorpoints for positional arguments.
        'events' list of pygame.events to compute.
        """
        # creating a new dict based on comparison of two
        self.config = validateDict(config, self.default)# dict
        self.name = self.config["name"]# str
        # declaring parent for positional properties
        self.parent = pg.display.get_surface().get_rect()# pygame.rect
        self.background = self.config["background"]# none / tuple
        self.rect = self.config["rect"]# pygame.rect
        self.anchors = getAnchors(self.rect.size)# dict
        self.events = []#list
        # building surface
        self.build()
    def build(self):
        """rebuilding everything."""
        # initiating surface
        pg.Surface.__init__(self, self.rect.size, pg.SRCALPHA)
        # updating anchors
        self.anchors = getAnchors(self.rect.size)
        # drawing
        if self.background:
            draw(self.background, self)
    def update(self):
        """
        run this method with each main loop. can be overwritten by the calling
            element.
        """
        pass
    def draw(self, object, rect=pg.Rect(0, 0, 0, 0)):
        """drawing something to the interface."""
        draw(object, self, rect)
    # events
    def mouseOver(self):
        """return 'true' if the mouse hovers the element."""
        mouse = pg.mouse.get_pos()
        hover = False

        #for event in events:
        if self.rect.collidepoint(mouse):
            hover = True

        return hover
    def leftClick(self):
        """returns 'true' if element is left-clicked."""
        mouse = pg.mouse.get_pos()
        click = False

        for event in self.events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if self.mouseOver():
                    click = True

        return click
class Interface(pg.Surface):
    """
    acts like a big surface to stat drawing the element tree from a json-file.
    """
    def __init__(self, name):
        """
        draws its size from the running window.
        'elements' a dict of all gui elements in the correct drawing order.
        'menus' a dict of all accessable menus of the interface ready to be
            called.
        'events' list of pygame.events. pass this trough every element to update
            it with momentum events.
        """
        # combine path + name to get the asset by its tail
        for js in loadAssets(PATH["interface"] + "\\" + name):# dict
            if js["type"] == "interface":
                self.config = js
        # taking rect from pygame.display
        self.rect = pg.display.get_surface().get_rect()# pygame.rect
        self.elements = {}# dict
        self.menus = {}# dict
        self.events = []# list / pygame.events
        # building surface / drawing
        self.build()
    def build(self):
        """
        building interface structure from file description. filling
            'self.elements' and 'self.menus' with gui elements.
        """
        # initiating surface
        pg.Surface.__init__(self, self.rect.size, pg.SRCALPHA)
        # filling 'self.elements' later with real element objects
        self.elements = {}
        self.menus = {}
        # creating menus
        if "menus" in self.config:
            for menu, prop in self.config["menus"].items():
                prop.update({"name": menu})
                #self.menus.append(convertElement(prop, self.rect))
                self.menus.update({
                    prop["name"]: convertElement(prop, self.rect)
                })
        # creating visible gui elements
        if "elements" in self.config:
            for elem in self.config["elements"]:
                e = convertElement(elem, self.rect)
                self.elements.update({
                    str(e.name): e
                })
        # drawing each element to interface
        for _, e in self.elements.items():
            draw(e, self, e.rect)
        # drawing menu if activated
        for m in self.menus:
            pass
    def draw(self, object, rect):
        """drawing something to the interface."""
        draw(object, self, rect)
    def resize(self, size):
        """
        set a new size for interface. needs to be rebuilt.
        'size' needs to be tuple.
        """
        # updating rect size
        self.rect.size = size
        # rebuilding
        self.build()
    def update(self, events):
        """run this method with each main loop. needs 'pygame.events' to run."""
        # updating internal events
        self.events = events

        for _, e in self.elements.items():
            # updating each element
            e.events = events
            e.update()
            # drawing elements to interface
            # reduced drawing functionallity to 'menubar' and 'infobar' for a
            # better fps performance
            if type(e) is MenuBar or type(e) is InfoBar:
                self.draw(e, e.rect)
            # drawing menus when activated
            if type(e) is MenuBar:
                # looking for buttons
                for elem in e.elements:
                    # if clicked set active and if clicked again rebuild
                    # interface
                    if elem.leftClick():
                        if not elem.state:
                            elem.state = True
                        else:
                            elem.state = False
                            self.build()
                    # if clicked somewhere else rebuild interface
                    elif not elem.mouseOver() and pg.mouse.get_pressed()[0]:
                        if elem.state:
                            elem.state = False
                            self.build()
                    # drawing depending on button state
                    if elem.state:
                        for name, menu in self.menus.items():
                            if name == elem.name:
                                # updating menus rect position
                                menu.rect.topleft = (
                                    elem.rect.left,
                                    elem.rect.top + elem.rect.height
                                )
                                # updating menu activation
                                menu.active = True
                                # drawing right under the menu point
                                self.draw(menu, menu.rect)
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
        'state' state of activation. 'true' on click.
        'hover' different color tuple for highlighting on 'hover' event.
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
    def update(self):
        """run this method with each main loop. needs 'pygame.events'."""
        # determining background
        if self.mouseOver():
            bg = self.hover
        # stays hover backgrounded if mouse moves out of button rect
        elif self.state:
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
class InfoBar(GuiMaster):
    """used for displaying information in a small bar."""
    def __init__(self, config={}):
        """
        'info' must be dict. is used to convert information into text later.
        """
        # inherit from gui master
        GuiMaster.__init__(self, config)
        # additional attributes
        self.info = {}# dict
        self.text = Text({# text object
            "text": "",
            "fontsize": 12
        })
    def update(self):
        """run this method with each main loop."""
        # building text to draw
        txt = ""
        for k, v in self.info.items():
            txt += k + ": " + str(v) + "    "
        self.text.update(text=txt)
        # drawing background and text to infobar
        self.draw(self.background, self.rect)
        self.draw(self.text, (
            10,
            self.anchors["middle"] - int(self.text.rect.height / 2)
        ))
class Menu(GuiMaster):
    """a menu with clickable elements to call menus from."""
    def __init__(self, config={}):
        """
        'elements' dict of elements to display and interact with.
        'active' shows 'true' if called.
        '__cfg' internal copy of the raw config dict. needed to get to menus
            elements.
        """
        # inherit from gui master
        GuiMaster.__init__(self, config)
        self.elements = {}# dict
        self.active = False# bool
        self.__cfg = config# dict
        self.__build()
    def __build(self):
        """creating the object."""
        # beginning with a fresh dict
        self.elements = {}

        # filling 'self.elements' with gui objects and draw them
        if "elements" in self.__cfg:
            for elem in self.__cfg["elements"]:
                elem = convertElement(elem, self.rect)
                self.elements.update({
                    elem.name: elem
                })

        # drawing
        y = 0
        for _, elem in self.elements.items():
            draw(elem, self, (self.rect.left, y))
            y += elem.rect.height
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
    def update(self):
        """run this method with each main loop. needs 'pygame.events'."""
        for elem in self.elements:
            # updating each element
            if type(elem) is Button:
                elem.events = self.events
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
class Text(GuiMaster):
    """text surface. ready to be drawn."""
    cfg = {
    	"font": FONTS["base"]["name"],
    	"fontsize": FONTS["base"]["size"],
    	"color": FONTS["base"]["color"],
        "background": None,
    	"text": "No Text",
    	"antialias": True,
    	"bold": False,
    	"italic": False,
        "rect": None,
        "wrap": False,
        "position": None
    }
    def __init__(self, config={}):
        """
        creates a text obejct that can be drawn to any surface.
        'fontsize' its in the name.
        'color' should be tuple by 3 like (50, 110, 95).
        'text' only one-liners right now.
        'antialias' if 'false' the font will appear pixelated.
        'font' creates a new pygame.font from an installed system font.
        'wrap' if 'true' then call a function to wrap the text into a given
            rect.
        'rect' dynamically using font-rect if there is no rect given as
            parameter.
        'position' positional argument of the text within the given rect if
            there is one. can be tuple (0, 0) list [0, 0] or str "center" etc.
        """
        # inherit from gui master
        GuiMaster.__init__(self, config)
        # comparing both dicts and creating a new one from it
        self.config = validateDict(config, self.cfg)# dict
        # initiating font module
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
        self.rect = self.config["rect"]# none / tuple / list
        self.position = self.config["position"]# none / tuple / list / str
        # building / drawing
        self.__build()
    def __build(self):
        """create the element."""
        # determine new size
        if not self.rect:
            size = self.font.size(self.text)
        else:
            size = self.rect.size
        # initiating surface
        pg.Surface.__init__(self, size, pg.SRCALPHA)
        # wrapped text
        if self.wrap:
            self.image = wrapText(
                self.text,
                self.color,
                pg.Rect((0, 0), self.rect.size),
                self.font,
                aa = self.antialias
            )
        # non-wrapped text
        else:
            self.image = self.font.render(
                self.text,
                self.antialias,
                self.color
            )
            self.rect = self.image.get_rect()
        # drawing background
        if self.background:
            self.draw(self.background)
        # determine position for text within the rect
        if self.position:
            pos = self.position
        else:
            pos = (0, 0)
        # drawing text
        self.draw(self.image, pos)
    def update(self, **kwargs):
        """run this method with each app loop."""
        if "text" in kwargs:
            self.text = kwargs["text"]
        self.__build()
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
class Window(GuiMaster):
    """a window pop up."""
    def __init__(self, config={}):
        """."""
        # inherit from gui master
        GuiMaster.__init__(self, config)
