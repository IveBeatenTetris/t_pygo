from .utils import (
    PATH,
    LIBPATH,
    FONTS,
    draw,
    validateDict,
    loadAssets,
    loadJSON,
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

        globals()["app"] = self
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
        "rect": pg.Rect(0, 0, 100, 100),
        "background": None,
        "hover": None
    }
    def __init__(self, config={}):
        """."""
        self.config = validateDict(config, self.default)# dict
        self.parent = pg.display.get_surface().get_rect()# pygame.rect
        if type(self.config["rect"]) is list:
            rect = pg.Rect(convertRect(self.config["rect"], self.parent))
        else:
            rect = self.config["rect"]
        self.rect = rect# pygame.rect
        self.anchors = getAnchors(self.rect.size)# dict
        if self.config["background"]:
            background = tuple(self.config["background"])
        else:
            background = self.config["background"]
        self.background = background# none / tuple
        if self.config["hover"]:
            hover = tuple(self.config["hover"])
        else:
            hover = self.config["hover"]
        self.backgroundhover = hover# none / tuple
        self.hover = False# bool
        self.click = False# bool
        #self.focus = False# bool
        self.build()
    def build(self):
        """."""
        pg.Surface.__init__(self, self.rect.size, pg.SRCALPHA)
        if self.background:
            self.draw(self.background)
    def draw(self, object, position=(0, 0)):
        """."""
        draw(object, self, position)
    def leftClick(self):
        """."""
        self.click = False

        if self.mouseOver() and pg.mouse.get_pressed()[0]:
            self.click = True

        return self.click
    def mouseOver(self):
        """."""
        mouse = pg.mouse.get_pos()
        self.hover = False

        #for event in events:
        if self.rect.collidepoint(mouse):
            self.hover = True

        return self.hover
    def resize(self, size):
        """."""
        self.rect.size = size
        self.anchors = getAnchors(self.rect.size)
        self.build()
    def update(self):
        """."""
        if self.mouseOver():
            if self.backgroundhover:
                self.draw(self.backgroundhover)
        else:
            if self.background:
                self.draw(self.background)
class Interface(pg.Surface):
    """."""
    default = {
        "app": None,
        "name": "Unnamed Element",
        "rect": pg.Rect(0, 0, 100, 100),
        "background": None,
        "hover": None
    }
    def __init__(self, name):
        """."""
        for js in loadAssets(PATH["interface"] + "\\" + name):# dict
            if js["type"] == "interface":
                self.cfg = js# dict
        self.config = validateDict(self.cfg, self.default)# dict
        self.parent = pg.display.get_surface().get_rect()# pygame.rect
        if type(self.config["rect"]) is list:
            rect = pg.Rect(convertRect(self.config["rect"], self.parent))
        else:
            rect = self.config["rect"]
        self.rect = rect# pygame.rect
        if self.config["background"]:
            background = tuple(self.config["background"])
        else:
            background = self.config["background"]
        self.background = background# none / tuple
        pg.Surface.__init__(self, rect.size)
        self.anchors = getAnchors(self.rect.size)# dict
        self.elements = self.createElements()# list
        self.build()
    def build(self):
        """."""
        pg.Surface.__init__(self, self.rect.size, pg.SRCALPHA)
        if self.background:
            self.draw(self.background)
    def createElements(self):
        """."""
        elements = []
        c = self.cfg

        if "elements" in c:
            for e in c["elements"]:
                if "type" in e:
                    if e["type"] == "panel":
                        elements.append(Panel(e))
                    elif e["type"] == "button":
                        e["position"] = "center"
                        elements.append(Button(e))
                    elif e["type"] == "menubar":
                        elements.append(MenuBar(e))
                    elif e["type"] == "infobar":
                        elements.append(InfoBar(e))

        return elements
    def draw(self, object, position=(0, 0)):
        """."""
        draw(object, self, position)
    def resize(self, size):
        """."""
        self.rect.size = size
        self.anchors = getAnchors(self.rect.size)
        self.elements = self.createElements()
        self.build()

        for e in self.elements:
            e.update()
            self.draw(e, e.rect)
    def update(self):
        """."""
        mrel = pg.mouse.get_rel()
        mpos = pg.mouse.get_pos()

        for e in self.elements:
            e.update()
            drawing = False

            if e.mouseOver():
                if mrel[0] != 0 or mrel[1] != 0:
                    drawing = True
                    e.update()

            if type(e) is Button:
                drawing = True
            elif type(e) is InfoBar:
                drawing = True
            elif type(e) is MenuBar:
                drawing = True
                for name, option in e.options.items():
                    if option.hover:
                        pass

            if drawing:
                self.draw(e, e.rect)
# all these following elements draw from GuiMaster
class Button(GuiMaster):
    """."""
    def __init__(self, config={}):
        """."""
        GuiMaster.__init__(self, config)
        if "position" in config:
            pos = config["position"]
        else:
            pos = (0, 0)
        self.textposition = pos# tuple
        self.text = Text(config)
    def update(self):
        """."""
        if self.mouseOver():
            if self.backgroundhover:
                self.draw(self.backgroundhover)
                self.draw(self.text, self.textposition)
        else:
            if self.background:
                self.draw(self.background)
                self.draw(self.text, self.textposition)
class InfoBar(GuiMaster):
    """."""
    def __init__(self, config={}):
        """."""
        GuiMaster.__init__(self, config)
        self.cfg = config# dict
        self.info = self.createInfo()# str
    def createInfo(self):
        """."""
        c = self.cfg
        info = ""

        if "info" in c:
            for i in c["info"]:
                if i == "mouse":
                    info += "Mouse: " + str(pg.mouse.get_pos()) + " "
                elif i == "appsize":
                    info += "AppSize: " + str(self.parent.size) + " "
                elif i == "fps":
                    info += "FPS: " + str(globals()["app"].fps) + " "

        return info
    def update(self):
        """."""
        bg = self.background

        self.info = self.createInfo()
        self.text = Text({# text object
            "text": self.info,
            "fontsize": 12
        })

        if self.mouseOver():
            if self.backgroundhover:
                bg = self.backgroundhover

        self.draw(bg)
        self.draw(self.text, (
            10,
            self.anchors["middle"] - int(self.text.rect.height / 2)
        ))
class Menu(GuiMaster):
    """."""
    def __init__(self, config={}):
        """."""
        GuiMaster.__init__(self, config)
class MenuBar(GuiMaster):
    """."""
    def __init__(self, config={}):
        """."""
        GuiMaster.__init__(self, config)
        self.cfg = config# dict
        self.options = {}# dict
        self.menus = self.createMenus()# dict
    def createMenus(self):
        """."""
        c = self.cfg
        options = {}
        menus = {}
        x = 0

        if "menus" in c:
            for name, m in c["menus"].items():
                m["x"] = x
                m["fontsize"] = 14
                m["name"] = name
                m["text"] = name
                m["background"] = self.background
                m["backgroundhover"] = self.backgroundhover
                self.options[name] = self.createOption(m)
                menus[name] = Menu(m)
                x += self.options[name].get_rect().width

        return menus
    def createOption(self, config):
        """."""
        text = Text({
            "text": config["text"],
            "fontsize": config["fontsize"]
        })
        size = (
            text.rect.width + 20,
            self.rect.height
        )
        #surface = pg.Surface(size, pg.SRCALPHA)
        surface = GuiMaster({
            "rect": [
                config["x"],
                0,
                text.rect.width + 20,
                self.rect.height
            ]
        })
        draw(text, surface, "center")

        return surface
    def update(self):
        """."""
        mouse = pg.mouse.get_pos()
        pos = [0, 0]

        if self.background:
            self.draw(self.background)

        for _, o in self.options.items():
            o.update()
            rect = o.get_rect()
            rect.topleft = pos
            if self.mouseOver():
                if rect.collidepoint(mouse):
                    if self.backgroundhover:
                        self.fill(self.backgroundhover, rect)
            self.draw(o, rect)
            pos[0] += o.get_rect().width
class Panel(GuiMaster):
    """."""
    def __init__(self, config={}):
        """."""
        GuiMaster.__init__(self, config)
class Text(GuiMaster):
    """."""
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
        "wrap": None,
        "position": (0, 0)
    }
    def __init__(self, config={}):
        """."""
        GuiMaster.__init__(self, config)
        config = validateDict(config, self.cfg)# dict

        self.text = config["text"]# str
        self.color = config["color"]# none / list / tuple
        self.antialias = config["antialias"]# bool
        self.wrap = config["wrap"]# none / int / tuple

        pg.font.init()
        self.font = pg.font.SysFont(# pygame.font
        	config["font"],
        	config["fontsize"]
        )
        self.font.set_bold(config["bold"])
        self.font.set_italic(config["italic"])

        self.recreate()
        self.draw(self.image)
    def recreate(self):
        """."""
        # resetting background
        self.background = None

        if not self.wrap:
            self.image = self.font.render(
                self.text,
                self.antialias,
                self.color
            )
            self.rect.size = self.image.get_rect().size
            self.build()
        else:
            if type(self.wrap) is int:
                rect = (0, 0, self.wrap, self.rect.height)
            elif type(self.wrap) is tuple:
                rect = (0, 0, self.wrap[0], self.wrap[1])

            self.image = wrapText(
                self.text,
                self.color,
                pg.Rect(rect),
                self.font,
                aa = self.antialias
            )
class Window(GuiMaster):
    """a window pop up."""
    def __init__(self, config={}):
        """."""
        # inherit from gui master
        GuiMaster.__init__(self, config)
# not yet converted
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
