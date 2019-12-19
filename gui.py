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
    """
    pygames window module with extended features. can be accessed by calling
        'globals()["app"]'.
    for the active event list use the internal one instead of calling the
        method 'events()' again to refresh events:
        'globals()["app"]._events' good.
        'globals()["app"].events()' bad.

    'defaults' is a dict of standard properties. on initiation the given
        parameter 'config' is beeing compared to the default dict. if some given
        properties are missing they are simply replaced with default values.
        the result is a validated dict to draw initiation instructions.
    """
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
        initiates pygame to act as an app window.

        'config' validated dict by comparison of a user set dict of properties
            and the elements default ones.
        'size' window size in a tuple for short reference only.
        'title' is gonna be displayed as the windows title.
        'icon' is displayed next to the title in the window.
        'clock' pygame clock for tracking fps.
        'preffered_fps' user defined maximal frames per second.
        'fps' is gonna be updated from the windows update-method.
        'paused' is a switch for showing a gui and closing it. handled by
            'self.pause()'.
        'mode' is for switching trough modes like 'moving' or 'paused'.
        'controller' decided to put it into the window. its been updated in the
            'window.events()'-method.
        'display' holds the actual pygame window.
        'screenshot' this surface can be used to simulate frozen screens like
            in menus. its refreshed by calling 'self.screenShot()'
        'fullscreen' if 'true' it renders the window maximized and borderless.
        'bgrepeat' str with either 'x' 'y' or 'xy'.
        'background' used to draw to background. might be 'str' or 'tuple'. if
            'string' then use it as image path and load a pygame.image surface.
        '_events' with each game-loop this list will become the new
            pygame.events. use this instead of calling 'app.events()'. this
            would only refresh the event list. resulting in loss of some events.
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
        # background related
        self.fullscreen = self.config["fullscreen"]# bool
        self.bgrepeat = self.config["backgroundrepeat"]# str
        self.background = self.__createBackground(# pygame.surface
            self.config["background"]
        )
        # event related
        self._events = []# list
        # adding app to globals for accessing out of boundaries
        globals()["app"] = self
    # game routines
    def update(self):
        """
        call this method on each main loop end to refresh its contents and
            visuals.
        """
        # refreshing display
        pg.display.update()
        # updating fps
        self.clock.tick(self.preffered_fps)
        self.fps = int(self.clock.get_fps())
    def quit(self):
        """exits the app."""
        pg.quit()
        sys.exit()
    def pause(self):
        """
        pauses the game or continues it. also freezes screen to simulate
            stopping by taking a display copied surface. internal property
            'self.paused' is gonna be togled on/off.
        """
        if self.paused is True:
            self.paused = False
        else:
            self.paused = True
            # make a screenshot
            self.screenshot = self.display.copy()
    # display stuff
    def __createBackground(self, bg):# pygame.surface
        """creates background based on background properties."""
        # declaring background type
        if type(bg) is str:
            bg = pg.image.load(bg)
        elif type(bg) is tuple:
            pass
        # checking background repeat
        if type(bg) is pg.Surface:
            if self.config["backgroundrepeat"]:
                # creating surfact with repeated background
                # 'bgrepeat' is the indicator ('x', 'y', 'xy')
                bg = repeatBG(
                    bg,
                    self.size,
                    self.bgrepeat
                )

        return bg
    def draw(self, object, position=(0, 0)):
        """draw something to windows 'display' surface."""
        draw(object, self.display, position)
    def resize(self, size=None):# bool
        """
        resizes the window.

        'size' needs to be a tuple. if no 'size parameter' is given this method
            serves as a 'resized-event' checker and returns 'true' or 'false'.
        """
        # on given parameter
        if size:
            # make new display surface
            self.display = getDisplay(# pygame.surface
                size,
                resizable = self.config["resizable"],
                fullscreen = self.fullscreen
            )
            # drawing background
            self.draw(self.background)
            # overwriting internal size (only for referencing)
            self.size = size
        # with no given parameter
        else:
            # return a tuple when resized or not
            resized = None

            for e in self._events:
                if e.type is pg.VIDEORESIZE:
                    resized = e.size

            return resized
    def screenShot(self, surface=None):# pygame.surface
        """
        makes a visual copy of the actual display and stores it in
            'self.screenshot'.
        if 'surface' is given then sotre a copy of that instead.
            """
        if surface:
            self.screenshot = surface.copy()
        else:
            self.screenshot = self.display.copy()

        return self.screenshot
    # event related methodes
    def events(self):# list
        """
        going trough some pygame events and returns a list of all active events.
        also updates the controller with events.
        """
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
    def pressedKeys(self):# list
        """return pygame-event's pressed keys (list)."""
        return pg.key.get_pressed()
    def keys(self):# dict
        """might look for a more efficient way to check for pressed keys."""
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
    def mouseWheel(self):# str
        """mouse wheel event checking. returns 'none' or str ('up', 'down')."""
        wheel = None

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
        """change the window title. 'title' should be a string."""
        if type(title) is not str:
            title = str(title)
        pg.display.set_caption(title)



class Master(pg.Surface):
    """."""
    defaults = {
        "background": None,
        "dragable": True,
        "size": (200, 150)
    }
    def __init__(self, config={}):
        """."""
        self.config = validateDict(config, self.defaults)# dict
        self.rect = pg.Rect((0, 0), self.config["size"])# pg.rect
        self.background = self.config["background"]# none / tuple / pg.surface
        self.dragable = self.config["dragable"]# bool
        self.dragged_at = None# none / tuple
        self.clicked = False# bool

        self.createSurface()
    def createSurface(self, **kwargs):
        """."""
        size = self.config["size"]

        if "size" in kwargs:
            size = kwargs["size"]

        pg.Surface.__init__(self, size, pg.SRCALPHA)
        self.rect = self.get_rect()

        if self.background:
            self.draw(self.background)
    def draw(self, object, rect=None):
        """."""
        if type(object) is tuple or type(object) is list:
            self.fill(object)
        elif not rect:
            rect = object.get_rect()
            self.blit(object, rect)
    # events and event checking
    def click(self):# bool
        """."""
        mpos = pg.mouse.get_pos()
        mbut = pg.mouse.get_pressed()
        clicked = False

        if self.rect.collidepoint(mpos) and mbut[0]:
            clicked = True

        return clicked
    def hover(self):# bool
        """."""
        mpos = pg.mouse.get_pos()
        mouse_over = False

        if self.rect.collidepoint(mpos):
            mouse_over = True

        return mouse_over
    def resize(self, size=None):
        """."""
        if size:
            self.createSurface(size=size)
        else:
            self.createSurface()
    def update(self):
        """."""
        mbut = pg.mouse.get_pressed()
        mpos = pg.mouse.get_pos()

        if self.dragable:
            for evt in globals()["app"]._events:
                if evt.type is pg.MOUSEBUTTONDOWN and self.hover():
                    if not self.clicked:
                        self.dragged_at = (
                            mpos[0] - self.rect.x,
                            mpos[1] - self.rect.y
                        )
                    self.clicked = True
                elif evt.type is pg.MOUSEBUTTONUP:
                    self.clicked = False
                    self.dragged_at = None

            if self.clicked:
                self.rect.topleft = (
                    mpos[0] - self.dragged_at[0],
                    mpos[1] - self.dragged_at[1]
                )
class UI(Master):
    """."""
    def __init__(self, name):
        """."""
        for js in loadAssets(PATH["interface"] + "\\" + name):# dict
            if js["type"] == "interface":
                self.cfg = js
        Master.__init__(self, self.cfg)

class GuiMaster(pg.Surface):
    """
    master-element for many gui elements to inherit from. comes with diverse
    events an additional properties/methodes for surfaces.
    use 'self.update()' to rfresh contents.

    'default' default properties for this object.
    """
    default = {
        "name": "Unnamed Element",
        "rect": pg.Rect(0, 0, 100, 100),
        "background": None,
        "hover": None,
        "drag": False,
        "visible": True
    }
    def __init__(self, config={}):
        """
        to see recently made changes to your analoge-created element you need to
            call its 'update()' method.

        'config' build instructions.
        'parent' window surface rect.
        'rect' elements dimensions. positional statements are:
            x,y
            top, left, bottom, right
            topleft, bottomleft, topright, bottomright
            midtop, midleft, midbottom, midright
            center, centerx, centery
            size, width, height
            w,h
        'background' can be 'none' or 'tuple'. used to fill the background of
            the surface with a color.
        'hoverbackground' surface background can be filled with this color if
            there is a given color tuple.
        'hover' bool - used for checking the hover-state of the mouse relative
            to the element.
        'click' same for this attribute. 'true' on click until not released.
        'dragable' used to check if the element is gonna be dragged and dropped.
        'draggedat' needed to calculate the elements rect position on dragging
            with mouse.
        'state' use this to check an elements activation state. works like a
            bool.
        'visible' can be used to toggle rendering of this menu.
        """
        # creating a dict based of comparison of config{} and default{}
        self.config = validateDict(config, self.default)# dict
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
        if self.config["hover"]:
            hover = tuple(self.config["hover"])
        else:
            hover = self.config["hover"]
        self.backgroundhover = hover# none / tuple
        self.hover = False# bool
        self.click = False# bool
        self.dragable = self.config["drag"]# bool
        self.draggedat = None# none / tuple
        self.state = "waiting"# str
        self.visible = self.config["visible"]# bool
        # building element
        self.build()
    def build(self):
        """building the element. can be overwritten by is calling gui member."""
        # reinitiating surface
        pg.Surface.__init__(self, self.rect.size, pg.SRCALPHA)
        # drawing background if there is one
        if self.background:
            self.draw(self.background)
    def draw(self, object, position=(0, 0)):
        """standard drawing method for elemenet. can be overwritten by user."""
        draw(object, self, position)
    def leftClick(self):# bool
        """
        returns the state of this element beeing left clicked or not. it also
            drags and drops the element if this is enabled by user. can but
            should not be overwritten by user.
        """
        mpos = pg.mouse.get_pos()
        mbut = pg.mouse.get_pressed()

        # looking for mousebutton events from pygame
        for evt in globals()["app"]._events:
            if self.mouseOver():
                # on press make dragable if necessary
                if evt.type is pg.MOUSEBUTTONDOWN:
                    self.click = True
                    if self.dragable:
                        self.draggedat = (
                            mpos[0] - self.rect.x,
                            mpos[1] - self.rect.y
                        )
                    # toggling state
                    if self.state == "waiting":
                        self.state = "active"
                # else set 'click' false and 'draggedat' none again
                elif evt.type is pg.MOUSEBUTTONUP:
                    self.click = False
                    if self.dragable:
                        self.draggedat = None
            # toggling state
            elif not self.mouseOver() and mbut[0]:
                if self.state == "active":
                    self.state = "waiting"
        # if dragable recalculate rect position
        if self.dragable and self.click:
            self.rect.topleft = (
                mpos[0] - self.draggedat[0],
                mpos[1] - self.draggedat[1]
            )

        return self.click
    def mouseOver(self):# bool
        """returns 'true' if mosue is over this element. can be overwritten."""
        mouse = pg.mouse.get_pos()
        self.hover = False

        if self.rect.collidepoint(mouse):
            self.hover = True

        return self.hover
    def resize(self, size):
        """
        resizeing the object by the given 'size' parameter. must be tuple of
            two ints. rebuilding element afterwards.
        """
        self.rect.size = size
        self.build()
    def toggle(self):
        """used to toggle 'self.state'."""
        if self.state == "waiting": s = "active"
        elif self.state == "active": s = "waiting"
        self.state = s
    def update(self):
        """
        run this method every main loop to auto update the elements visuals.
        usually redraws the background on mouse hover if 'self.backgroundhover'
            is defined.
        can be overwritten by user but also iverwrites auto-background-applying.
        """
        if self.mouseOver():
            if self.backgroundhover:
                self.draw(self.backgroundhover)
        else:
            if self.background:
                self.draw(self.background)
class Interface2(GuiMaster):
    """."""
    def __init__(self, name):
        """."""
        for js in loadAssets(PATH["interface"] + "\\" + name):# dict
            if js["type"] == "interface":
                self.cfg = js# dict
        self.cfg["rect"] = globals()["app"].display.get_rect()
        GuiMaster.__init__(self, self.cfg)
        self.elements = self.loadElements()# dict
        self.drawElements()
    def drawElements(self, element=None):
        """."""
        if element:
            e = self.elements[element]
            e.update()
            self.draw(e, e.rect)
        else:
            for n, e in self.elements.items():
                e.update()
                self.draw(e, e.rect)
    def drawMenu(self, menu):
        """."""
        for _, e in self.elements.items():
            if type(e) is MenuBar:
                m = e.menus[menu]
                self.draw(m, m.rect)
    def loadElements(self, element=None):
        """."""
        elements = {}
        c = self.cfg

        if "elements" in c:
            # if there is a given element
            if element:
                pass
            # with no specific element given
            else:
                i = 1
                for e in c["elements"]:
                    # adding 'name' property to config dict for the element
                    if not "name" in e:
                        name = "Unnamed" + str(i)
                        i += 1
                    else:
                        name = e["name"]
                    # looking for 'type' property
                    if "type" in e:
                        # adding elements depending on type
                        if e["type"] == "panel":
                            elements[name] = Panel(e)
                        elif e["type"] == "button":
                            elements[name] = Button(e)
                        elif e["type"] == "menubar":
                            elements[name] = MenuBar(e)
                        elif e["type"] == "infobar":
                            elements[name] = InfoBar(e)

        return elements
    def resize(self, size=None):
        """."""
        if size:
            self.rect.size = size
        self.build()
        self.elements = self.loadElements()
        self.drawElements()
    def update(self):
        """."""
        mpos = pg.mouse.get_pos()
        mbut = pg.mouse.get_pressed()

        for n, e in self.elements.items():
            if type(e) is InfoBar:
                self.drawElements(n)
            elif type(e) is MenuBar:
                self.drawElements(n)
                for name, o in e.options.items():
                    menu = e.menus[name]

                    if o.leftClick():
                        menu.visible = True
                    else:
                        menu.visible = False

                    if menu.visible:
                        # resizing here to clear the menu for drawing a new one
                        self.resize()
                        self.drawMenu(name)

            elif type(e) is Panel:
                pass
            elif (
                e.rect.collidepoint(mpos) and not e.hover or
                not e.rect.collidepoint(mpos) and e.hover or
                e.leftClick()
            ):
                self.drawElements(n)
# all these following elements draw from 'GuiMaster'
class Interface(GuiMaster):
    """
    this object serves as a big screen surface to draw all its gui elements on.
    the final product can then simply be drawn to the apps display surface.
    """
    def __init__(self, name):
        """
        uses 'guimaster' as its parent with additional methodes and attributes.

        'elements' a dict of elements to read and draw.
        """
        for js in loadAssets(PATH["interface"] + "\\" + name):# dict
            if js["type"] == "interface":
                self.cfg = js# dict
        GuiMaster.__init__(self, self.cfg)
        self.elements = self.createElements()# dict
        # first time creating visual surface
        self.recreate()
    def createElements(self, element=None):#dict
        """
        returns a dict of allready initiated gui elements ready to been drawn.
        'c' simply acts as the dict pulled from a json-file accessed by a name.
        user can pass a specific element to use this for recreation of single
            elements.
        """
        elements = {}
        c = self.cfg
        i = 1

        if "elements" in c:
            # if there is a given element
            if element:
                pass
            # with no specific element given
            else:
                for e in c["elements"]:
                    # adding 'name' property to config dict for the element
                    if not "name" in e:
                        name = "Unnamed" + str(i)
                        i += 1
                    else:
                        name = e["name"]
                    # looking for 'type' property
                    if "type" in e:
                        # adding elements depending on type
                        if e["type"] == "panel":
                            elements[name] = Panel(e)
                        elif e["type"] == "button":
                            elements[name] = Button(e)
                        elif e["type"] == "menubar":
                            elements[name] = MenuBar(e)
                        elif e["type"] == "infobar":
                            elements[name] = InfoBar(e)

        return elements
    def recreate(self, element=None):
        """
        rebuilding the displayable surface. 'element' must be the name of the
            element you want to recreate (string). if none is given then
            recreate everything.
        """
        mrel = pg.mouse.get_rel()
        mpos = pg.mouse.get_pos()

        # if 'element' name is given
        if element:
            e = self.elements[element]
            e.update()
            self.draw(e, e.rect)
        else:
            # drawing background if there is one given
            if self.background:
                self.draw(self.background)
            # for every element
            for _, e in self.elements.items():
                e.update()
                self.draw(e, e.rect)
    def resize(self, size):
        """
        overwriting parental 'resize()' method to act individually.
        resizes the surface and rebuilds it afterwards. 'size' needs to be a
            tuple of two ints.
        """
        # updating rect
        self.rect.size = size
        # rebuilding structure
        self.build()
        # recreating elements for adjusting in sizes
        self.elements = self.createElements()
        # recreating the visual output (one image in the end)
        self.recreate()
    def update(self):
        """
        overwriting parental 'update()' method to act individually.
        event checking and recreating of elements is bound to some conditions
            to reduce fps on an ever drawing surface.
        """
        # mouse events
        mpos = pg.mouse.get_pos()
        mrel = pg.mouse.get_rel()
        mbut = pg.mouse.get_pressed()

        # cycling trough elements
        for name, e in self.elements.items():
            # if this is set 'true' then the element will be drawn again
            recreate = False

            if type(e) is Panel:# conditional
                # only on click inside or outside
                if e.leftClick():
                    recreate = True
            elif type(e) is InfoBar:# unconditional
                recreate = True
            elif type(e) is MenuBar:# conditional
                for n, o in e.options.items():
                    # invoking left click so the state can toggle
                    o.leftClick()
                    # shortcut to named menu
                    m = e.menus[n]
                    # triggering menu visibility
                    if o.state == "active" and not m.visible:
                        m.visible = True
                    elif o.state == "waiting" and m.visible:
                        m.visible = False
                # tweaking menubar.rect on +1px for height so we can check if
                # the mouse leaves the rect and update its contents. its not
                # even visbile. it only serves the purpose for mouse hover
                phantom_rect = e.rect
                phantom_rect.height += 1
                # only render if mouse hovers and moves
                if phantom_rect.collidepoint(mpos):
                    if mrel[0] != 0 or mrel[1] != 0:
                        recreate = True
            elif type(e) is Button:# conditional
                # only recreate on first time hovering in out or on click
                # click also invokes the drag functionallity
                if (
                    e.rect.collidepoint(mpos) and not e.hover or
                    not e.rect.collidepoint(mpos) and e.hover or
                    e.leftClick()
                ):
                    recreate = True

            # only recreate element if condition matched previously
            if recreate:
                e.update()
                self.recreate(name)
            # drawing visible menus
            if type(e)is MenuBar:
                for n, m in e.menus.items():
                    # option shortcut
                    o = e.options[n]
                    # if option clicked
                    if o.click:
                        # toggle visible and draw its menu
                        m.visible = True
                        self.draw(m, m.rect)
                    # if clicked somehwere else while option is still visible
                    if mbut[0] and m.visible:
                        m.visible = False
class Button(GuiMaster):
    """
    resembles a button element with a text and common mouse interactive events.

    'cfg' default properties for this object.
    """
    cfg = {
        "margin": 20,
        "textposition": "center"
    }
    def __init__(self, config={}):
        """
        uses 'guimaster' as its parent with additional methodes and attributes.

        'cfg' need some additional properties from user.
        'margin' auto margin applying to text position so it doesnt look
            crunchy.
        'textposition' standard is 'center'. can also be tuple of two ints.
        'text' a buttons text object ready to been drawn.
        'rect' overwriting original rect if user has given his own.
        """
        GuiMaster.__init__(self, config)
        # creating a dict based of comparison of config{} and default{}
        self.cfg = validateDict(config, self.cfg)# dict
        # additional attributes
        self.margin = self.cfg["margin"]# int / list
        self.textposition = self.cfg["textposition"]# str / tuple
        self.text = Text(config)
        # translating rect if it has 'auto' or percentage strings
        if "rect" in config:
            self.rect = convertRect(config["rect"], self.text.rect)
            self.calcTextPos()
        # rebuilding surface to apply new rect
        self.build()
    def calcTextPos(self):
        """recalculates buttons size and its texts position in it."""
        if type(self.margin) is int:
            self.rect.width += self.margin
            self.rect.height += self.margin
    def update(self):
        """
        overwrites the standard method. call this method everytime you need to
            refresh the element.
        """
        # on mouse over look for different color
        if self.mouseOver():
            if self.backgroundhover:
                self.draw(self.backgroundhover)
        # look for standard background
        else:
            if self.background:
                self.draw(self.background)
        # redraw text anyways
        self.draw(self.text, self.textposition)
class InfoBar(GuiMaster):
    """
    this bar is used for displaying usefull information about the app and its
        contents.
    """
    def __init__(self, config={}):
        """
        uses 'guimaster' as its parent with additional methodes and attributes.

        'cfg' building instructions to draw from. it also declares what to
            display.
        'info' str of the information to display.
        """
        GuiMaster.__init__(self, config)
        self.cfg = config# dict
        self.info = ""# str
    def createInfo(self):# str
        """
        creation of information to display. returns a str.
        """
        c = self.cfg
        info = ""

        # reading user defined information to display
        if "info" in c:
            for i in c["info"]:
                if i == "mouse":
                    info += "Mouse: " + str(pg.mouse.get_pos()) + "     "
                elif i == "appsize":
                    info += "AppSize: " + str(self.parent.size) + "     "
                elif i == "fps":
                    info += "FPS: " + str(globals()["app"].fps) + "     "

        return info
    def update(self):
        """overwrites parental 'update()' method. calling to refresh element."""
        bg = self.background
        # recreating info text
        self.info = self.createInfo()
        # creating text object
        self.text = Text({# text object
            "text": self.info,
            "fontsize": 12
        })
        # on mouse over determine another background to draw if set
        if self.mouseOver():
            if self.backgroundhover:
                bg = self.backgroundhover
        # drawing background and info text
        self.draw(bg)
        self.draw(self.text, (
            10,
            int(self.rect.height / 2) - int(self.text.rect.height / 2)
        ))
class Menu(GuiMaster):
    """a dropdown menu with clickable options."""
    def __init__(self, config={}):
        """
        uses 'guimaster' as its parent with additional methodes and attributes.
        """
        GuiMaster.__init__(self, config)
class MenuBar(GuiMaster):
    """a menu bar object with several elements to click at."""
    def __init__(self, config={}):
        """
        uses 'guimaster' as its parent with additional methodes and attributes.

        'cfg' this dict holds building instructions for the menubar and its
            options.
        'menus' a dict of dropdown menus to call on a specific option.
        'options' a dict of buttons representing options of the menubar.
        """
        GuiMaster.__init__(self, config)
        self.cfg = config# dict
        self.menus = {}# dict
        self.options = self.createOptions()# dict
        # drawing first time
        for _, o in self.options.items():
            self.draw(o, o.rect)
    def createOptions(self):
        """
        creates buttons for the menubar to click at as well as theyre
            corresponding menus.
        """
        c = self.cfg
        options = {}

        if "menus" in c:
            # using 'x' to determine horizontal drawing position
            x = 0
            for name, o in c["menus"].items():
                # making button.rect slightly bigger
                but = Button({
                    "text": name,
                    "background": self.background,
                    "hover": (55, 55, 65)
                })
                but.rect = pg.Rect(
                    x, self.rect.top,
                    but.text.rect.width + but.margin,
                    self.rect.height
                )
                # updating visuals
                but.build(); but.update()
                # appending to options dict
                options[name] = but
                # crafting option-button related menus
                self.menus[name] = Menu({
                    "background": (45, 45, 55),
                    "visible": False,
                    "rect": [
                        x,
                        self.rect.bottom,
                        150,
                        250
                    ]
                })

                # raising value of x
                x += but.rect.width

        return options
    def update(self):
        """
        overwrites parental method. used to redraw background updating options
            properties checks its events and draws the option to the menubar.
        """
        mpos = pg.mouse.get_pos()
        mrel = pg.mouse.get_rel()

        for _, o in self.options.items():
            # refreshing visuals and drawing afterwards
            o.update()
            self.draw(o, o.rect)
class Panel(GuiMaster):
    """."""
    def __init__(self, config={}):
        """."""
        GuiMaster.__init__(self, config)
class Text(GuiMaster):
    """
    a displayable text object.

    'cfg' properties for this object.
    """
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
        """
        uses 'guimaster' as its parent with additional methodes and attributes.
        """
        GuiMaster.__init__(self, config)
        # creating a new validated dict to read and build from
        config = validateDict(config, self.cfg)# dict
        # additional attributes
        self.text = config["text"]# str
        self.color = config["color"]# none / list / tuple
        self.antialias = config["antialias"]# bool
        self.wrap = config["wrap"]# none / int / tuple
        # initiating and adjusting pygame.font
        pg.font.init()
        self.font = pg.font.SysFont(# pygame.font
        	config["font"],
        	config["fontsize"]
        )
        self.font.set_bold(config["bold"])
        self.font.set_italic(config["italic"])
        # calling 'recreate()' as a way to build the text object
        self.recreate()
    def recreate(self):
        """used to rebuild the text object."""
        # resetting background tweak
        self.background = None
        # without wrapping properties
        if not self.wrap:
            # creating non-wrapped text here
            self.image = self.font.render(
                self.text,
                self.antialias,
                self.color
            )
            self.rect.size = self.image.get_rect().size
            self.build()
        # with wrapping properties
        else:
            # if a int is given then use it as width parameter for wrapping
            if type(self.wrap) is int:
                rect = (0, 0, self.wrap, self.rect.height)
            # if tuple of two ints then use both as wwidth and height statement
            elif type(self.wrap) is tuple:
                rect = (0, 0, self.wrap[0], self.wrap[1])
            # creating wrapped text here
            self.image = wrapText(
                self.text,
                self.color,
                pg.Rect(rect),
                self.font,
                aa = self.antialias
            )
        # drawing text image to text object surface
        self.draw(self.image)
class Window(GuiMaster):
    """a window pop up."""
    def __init__(self, config={}):
        """
        uses 'guimaster' as its parent with additional methodes and attributes.
        """
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
