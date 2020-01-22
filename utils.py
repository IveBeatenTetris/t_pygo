# dependencies
import json, os, re, ctypes, pprint
import xml.etree.ElementTree as et
import pygame as pg

# centering window
os.environ["SDL_VIDEO_CENTERED"] = "1"

# project and library pathes
PATH = {
    "go": os.path.dirname(__file__),
    "sysimg": os.path.dirname(__file__) + "\\images",
    "root": os.getcwd(),
    "assets": os.getcwd() + "\\assets",
    "images": os.getcwd() + "\\assets\\images",
    "maps": os.getcwd() + "\\assets\\maps",
    "tilesets": os.getcwd() + "\\assets\\tilesets",
    "entities": os.getcwd() + "\\assets\\entities",
    "interface": os.getcwd() + "\\assets\\interface"
}
LIBPATH = {
    "noimage": PATH["sysimg"] + "\\noimage.png",
    "notile": PATH["sysimg"] + "\\notile.png",
    "windowbg": PATH["sysimg"] + "\\bg01.png",
    "windowicon": PATH["sysimg"] + "\\ente.png",
    "dragging": PATH["sysimg"] + "\\dragging.png"
}
# app related
RESOLUTIONS = {
    "1920x1080": (1920, 1080),
    "800x400": (800, 400)
}
FONTS = {
    "base": {
        "name": "ebrima",
        "size": 16,
        "color": (200, 200, 200)
    },
    "sub": {
        "name": "verdana",
        "size": 14,
        "color": (200, 200, 200)
    },
    "special": {
        "name": "console",
        "size": 20,
        "color": (200, 200, 200)
    }
}
STYLE = {
    "app": {
        "size": (320, 240),
        "title": "Unnamed Project",
        "resizable": False,
        "fullscreen": False,
        "background_color": None,
        "background_image": LIBPATH["windowbg"],
        "background_repeat": None,
        "icon": LIBPATH["windowicon"],
        "fps": 30
    },
    "none": {
        "size": (300, 200),
        "position": (0, 0),
        "background_color": None,
        "background_hover": None,
        "border": False,
        "border_color": (0, 0, 0),
        "border_size": 1,
        "dragable": False,
        "drag_area": None,
        "drag_area_background": (45, 45, 55)
    },
    "button": {
        "text": "New Button",
        "font": FONTS["base"]["name"],
        "font_size": FONTS["base"]["size"],
        "color": FONTS["base"]["color"],
        "size": (100, 25),
        "position": (0, 0),
        "background_color": (30, 30, 40),
        "background_hover": (40, 40, 50),
        "border": True,
        "border_size": 1,
        "border_color": (10, 10, 20),
        "dragable": False,
        "drag_area": None,
        "drag_area_background": (45, 45, 55),
        "bold": False,
        "italic": False,
        "antialias": True,
        "shadow": None,
        "wrap": None,
        "padding": 10
    },
    "panel": {
        "size": (150, 200),
        "position": (0, 0),
        "background_color": (50, 50, 60),
        "background_hover": None,
        "border": False,
        "border_color": (0, 0, 0),
        "border_size": 1,
        "dragable": False,
        "drag_area": None,
        "drag_area_background": (70, 70, 80)
    },
    "table": {
        "size": (150, 50),
        "position": (0, 0),
        "background_color": (50, 50, 60),
        "background_hover": None,
        "border": True,
        "border_color": (10, 10, 20),
        "border_size": 1,
        "dragable": False,
        "drag_area": None,
        "drag_area_background": (70, 70, 80),
        "text_size": 12,
        "rows": ()
    },
    "slider": {
        "size": (150, 20),
        "position": (0, 0),
        "background_color": None,
        "background_hover": None,
        "border": False,
        "border_color": (0, 0, 0),
        "border_size": 1,
        "dragable": False,
        "drag_area": None,
        "alignment": "horizontal"
    },
    "slider_rail": {
        "size": (20, 20),
        "position": (0, 0),
        "background_color": (25, 25, 35)
    },
    "slider_handle": {
        "size": (20, 20),
        "position": (0, 0),
        "background_color": (50, 50, 60)
    },
    "slot": {
        "size": (60, 32),
        "position": (0, 0),
        "background_color": (45, 45, 55),
        "background_hover": (60, 60, 70),
        "border": True,
        "border_color": (10, 10, 20),
        "border_size": 1,
        "dragable": False,
        "drag_area": None
    },
    "text": {
        "size": (0, 0),
        "position": (0, 0),
        "font": FONTS["base"]["name"],
        "font_size": FONTS["base"]["size"],
        "color": FONTS["base"]["color"],
        "background_color": None,
        "background_hover": None,
        "dragable": False,
        "drag_area": None,
        "border": None,
        "text": "Text",
        "antialias": True,
        "bold": False,
        "italic": False,
        "shadow": None,
        "wrap": None,
        "padding": 0
    },
    "text_field": {
        "text": "New Textfield",
        "font": FONTS["base"]["name"],
        "font_size": FONTS["base"]["size"],
        "color": FONTS["base"]["color"],
        "size": (175, 30),
        "position": (0, 0),
        "background_color": (50, 50, 60),
        "background_hover": (60, 60, 70),
        "border": True,
        "border_size": 1,
        "border_color": (10, 10, 20),
        "dragable": False,
        "drag_area": None,
        "drag_area_background": (45, 45, 55),
        "bold": False,
        "italic": False,
        "antialias": True,
        "shadow": None,
        "wrap": None,
        "padding": 10
    },
    "text_cursor": {
        "size": (1, 30),
        "position": (2, 0),
        "color": (100, 100, 150)
    },
    "menu": {
        "size": (50, 75),
        "position": (0, 0),
        "background_color": (55, 55, 65),
        "background_hover": (35, 35, 45),
        "border": False,
        "border_color": (0, 0, 0),
        "border_size": 1,
        "dragable": False,
        "drag_area": None,
        "drag_area_background": (45, 45, 55),
        "options" : [],
        "margin": [7, 35, 7, 10]
    }
}

# rules for json parsing
json_comments =  re.compile(
    "(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?",
    re.DOTALL | re.MULTILINE
)

# console
def prettyPrint(data):
    """pretty-printing."""
    pprint.pprint(data)
# system
def getMachineResolution():# tuple
    """return full screen resolution in pixels."""
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    size = (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))
    return size
# files & directories
def loadAssets(path):# list
    """
    walks the assets-directory and opens each json or xml file. plus appending
        file name and file path to the returning list.
    """
    list = []

    # start walking
    for dirs in os.walk(path):
        # for every directory
        for each in dirs[2]:
            # split filename
            t = each.split(".")[1]

            if t == "json":
                config = loadJSON(dirs[0] + "\\" + each)
            elif t == "xml":
                config = loadXML(dirs[0] + "\\" + each)
                config = convertXmlToDict(config)
            # if directory has an image
            elif t == "png":
                config = {
                    "name": each.split(".")[0],
                    "type": "image",
                    "filepath": dirs[0]
                }
            # adding opened file-name to the dict as reference
            config.update({"filename": each})
            # appending to returning list
            list.append(config)

    return list
def loadJSON(path):# dict
    """load and convert a JSON file to a dict."""
    with open(path) as text:
        content = "".join(text.readlines())
        #looking for comments
        match = json_comments.search(content)
        while match:
            #single line comment
            content = content[:match.start()] + content[match.end():]
            match = json_comments.search(content)
        js = json.loads(content)
        if "name" in js:
            name = js["name"]
        else:
            name = path.split("\\")[-2]
        js.update({"name": name})
        js.update({"path": path})
        # //TODO tidy up
        s = path.split("\\")
        s = os.path.join(*s, "\\", *s[1:-1])
        js.update({"filepath": s})
        js.update({"filename": path.split("\\")[-1]})

    return js
def loadXML(path):
    """
    returns a 'xml.etree.ElementTree.ElementTree' object read from a xml file
        or object-type.
    """
    return et.parse(path)
# convering data types
def convertXmlToDict(xml):# dict
    """converts an xml.elementtree object into da dict and returns it."""
    def convertAttribute(l):# list
        """returns a dict made out of an xml.elementtree."""
        # 'none' so we can check if it doesnt apply correctly somewhere
        attribute = None

        # split to check its contents
        l = l.split(", ")
        # if list has a single value
        if len(l) == 1:
            # if  resembles an int
            if l[0].isdigit():
                # overwriting single int with a real single int
                attribute = int(l[0])
            # if its a str
            else:
                # check if attribute is bool
                if l[0] == "true" or l[0] == "True":
                    attribute = True
                elif l[0] == "false" or l[0] == "False":
                    attribute = False
                # return simple string
                else:
                    attribute = l[0]
        else:
            nl = []
            # for every item in the splitted list
            for e in l:
                # if item doesnt represent an integer
                if not e.isdigit():
                    # if last letter is '%'
                    if e[-1] == "%":
                        pass
                else:
                    # make item an integer
                    e = int(e)
                # append to temporary list
                nl.append(e)
            # this attributes gonna be a list
            attribute = nl

        return attribute
    def convertChildren(children):# list
        """returns a list children elements. works recursively."""
        c = []

        # cycling through elements
        for elem in children:
            # always starting with a type and predefined element list
            child = {}
            child["type"] = elem.tag
            # convert attributes to make it suitable for our structure
            for k, v in elem.attrib.items():
                child[k] = convertAttribute(v)
            # converting children elements again
            child["elements"] = convertChildren(elem.getchildren())
            # appending fresh child to returning list
            c.append(child)

        return c
    d = {}
    # predicting root and its children elements
    root = xml.getroot()
    elements = root.getchildren()
    # starting describing the dict
    d["type"] = root.tag
    # converting attributes to go-usable content
    for k, v in root.attrib.items():
        # adding value to returning dict
        d[k] = convertAttribute(v)
    # creating children sub nodes
    d["elements"] = convertChildren(elements)

    return d
def validateDict(config={}, defaults={}):# dict
    """
    validate a dictionary by comparing it to the default values from another
    given dict.
    """
    validated = {}

    for each in defaults:
        try:
            validated[each] = config[each]
        except KeyError:
            validated[each] = defaults[each]

    return validated
# pygame related
def convertRect(rect, parent):# pg.rect
    """
    returns a pygame.rect converted from the given rect like object.
    'parent' must be a pygame.rect.
    'rect' can be pygame.rect or list of 4. each value can be simple 'int' or a
        'str'.
    the values for positional arguments (0, 1) are:
        'left'
        'right'
        'top'
        'bottom'
    values for size arguments can be an integer or a string ('auto' or 'i%').
    example rects:
        rect = ["left", 30, "100%", 150]
        rect = [0, "top", 50, "90%"]
        rect = [250, "bottom", "auto", "90%"]
    """
    # this one is gonna be updated and converted to a pygame.rect on returning
    new_rect = [0, 0, 0, 0]
    # width
    if type(rect[2]) is int:
        new_rect[2] = rect[2]
    elif type(rect[2]) is str:
        if rect[2] == "auto":
            new_rect[2] = parent.width
        elif rect[2][-1] == "%":
            # convert to int
            percent = int(rect[2].split("%")[0])
            # overwriting cfg rect width
            new_rect[2] = parent.width * percent / 100
    # height
    if type(rect[3]) is int:
        new_rect[3] = rect[3]
    elif type(rect[3]) is str:
        if rect[3] == "auto":
            new_rect[3] = parent.height
        elif rect[3][-1] == "%":
            # convert to int
            percent = int(rect[3].split("%")[0])
            # overwriting cfg rect height
            new_rect[3] = parent.height * percent / 100
    # x
    if type(rect[0]) is int:
        new_rect[0] = rect[0]
    elif type(rect[0]) is str:
        # overwriting cfg rect x
        if rect[0] == "left":
            new_rect[0] = 0
        elif rect[0] == "right":
            new_rect[0] = parent.width - new_rect[2]
    # y
    if type(rect[1]) is int:
        new_rect[1] = rect[1]
    elif type(rect[1]) is str:
        # overwriting cfg rect y
        if rect[1] == "top":
            new_rect[1] = 0
        elif rect[1] == "bottom":
            new_rect[1] = parent.height - new_rect[3]

    return pg.Rect(new_rect)
def createTiledMap(config, tiles):# dict
    """
    drawing tiles on a pygame surface and returning it in a dict together with
    a list of wall rects and other special blocks with their position.
    """
    tilesize = tiles[0].image.get_rect().size

    blocks = []
    surface = pg.Surface(
        (
            config["width"] * tilesize[0],
            config["height"] * tilesize[1]
        ),
        pg.SRCALPHA)
    playerstart = None

    i = 0
    for row in range(config["height"]):
        y = row * tilesize[1]
        for line in range(config["width"]):
            x = line * tilesize[0]

            # only draw tile if area isn't empty
            if config["data"][i] != 0:
                tile = tiles[config["data"][i] - 1]
                rect = pg.Rect((x, y), tile.image.get_rect().size)
                # only draw if the tile is visible
                if tile.visible is True:
                    surface.blit(tile.image, (x, y))
                # add a block rect to blocklist if tile is not passable
                if tile.block:
                    blocks.append(rect)

                # set player-start position if there is a tile placed for that
                if tile.name:
                    if tile.name == "player_start":
                        playerstart = rect

            i += 1

    return {
        "image": surface,
        "blocks": blocks,
        "player_start": playerstart
    }
def draw(object, destination, rect=None, blendmode=0):# pg.surface
    """
    drawing a single or multiple objects to the destination surface. then
    return itself. 'rect' can be tuple, pygame.rect or a string.
    'special_flags' is for optional surface blending on each other.
    usage:
    draw(
        player,
        display,
        pygame.Rect(0, 0, 160, 120),
        special_flags=pygame.BLEND_ADD
    )
    """
    if type(rect) is str:
        # draw object in the relative to the given string
        if rect == "center":
            try:
                osize = object.get_rect().size
            except AttributeError:
                osize = object.image.get_rect().size
            dsize = destination.get_rect().size

            x = int(dsize[0] / 2) - int(osize[0] / 2)
            y = int(dsize[1] / 2) - int(osize[1] / 2)
            #rect = (x, y)
            rect = pg.Rect(x, y, osize[0], osize[1])

    # recursively drawing depending on object's type by calling this function
    # again
    if type(object) is tuple:
        destination.fill(
            object, destination.get_rect(),
            rect,
            special_flags=blendmode
        )
    elif type(object) is list:
        for each in object:
            draw(each, destination, rect, blendmode=blendmode)
    elif type(object) is dict:
        for each in object:
            destination.blit(object[each], rect)
    elif (
        object.__class__.__bases__[0] is pg.Surface or
        type(object) is pg.Surface or
        issubclass(type(object), pg.Surface)
    ):
        destination.blit(object, rect, special_flags=blendmode)
    elif object.__class__.__bases__[0] is pg.sprite.Sprite:
        destination.blit(object.image, rect, special_flags=blendmode)
    elif object.__class__ is pg.sprite.Group:
        for sprite in object:
            destination.blit(
                sprite.image,
                sprite.rect,
                special_flags=blendmode
            )
    # might puke out an error on giving anything else than pg.sprite.Sprite
    else:
        destination.blit(object.image, rect)

    return destination
def drawBorder(surface, **kwargs):
    """
    draws a border on the given surface-object and returns it.
    keyword-arguments can be:
        'size'  (int)           :   declares how big the line-size draws the
                                    border.
        'color' (tuple/list)    :   the line-color of the border requiring 3
                                    integers to resemble a color-argument.
        'rect'  (pg.rect/tuple/ :   if this is not given, use the surface's
                list)               dimensions instead.
    example:
        config = (1, (255, 255, 255), [5, 10, 100, 25])
    usage:
        config = (3, (0, 0, 0))
        surf = drawBorder(display, size=config[0], color=config[1])
    """
    # creating a standard-setup for the border
    cfg = validateDict(kwargs, {
        "size"      :   1,
        "color"     :   (0, 0, 0),
        "rect"      :   surface.get_rect()
    })
    # converting into pygame.rect if it's a list or a tuple
    if type(cfg["rect"]) is list or type(cfg["rect"]) is tuple:
        cfg["rect"] = pg.Rect(cfg["rect"])
    # drawing border to the background
    pg.draw.lines(
        surface,
        cfg["color"],
        False,
        [
            cfg["rect"].topleft,
            (cfg["rect"].left, cfg["rect"].height - 1),
            (cfg["rect"].width - 1, cfg["rect"].height - 1),
            (cfg["rect"].width - 1, cfg["rect"].top),
            cfg["rect"].topleft,
        ],
        cfg["size"]
    )

    return surface
def getAnchors(room):# dict
    """returns a dict of room's anchor-points."""
    anchors = {
        "top": 0,
        "middle": int(room[1] / 2),
        "bottom": room[1],
        "left": 0,
        "center": int(room[0] / 2),
        "right": room[0],
        "topleft": (0, 0),
        "topcenter": (int(room[0] / 2), 0),
        "topright": (room[0], 0),
        "midleft": (0 , int(room[1] / 2)),
        "midcenter": (int(room[0] / 2), int(room[1] / 2)),
        "midright": (room[0], int(room[1] / 2)),
        "bottomleft": (0, room[1]),
        "bottomcenter": (int(room[0] / 2), room[1]),
        "bottomright": (room[0], room[1])
    }
    return anchors
def getDisplay(size, **kwargs):# pg.display.surface
    """
    create a new window display and return it. customisation possible.
    example: resizable = True
    usage: screen = getDisplay(((1920, 1080), resizable = True))
    """
    for key, value in kwargs.items():
        if key == "fullscreen":
            if value is True:
                display = pg.display.set_mode(size, pg.FULLSCREEN)
        elif key == "resizable":
            if value is True:
                display = pg.display.set_mode(size, pg.RESIZABLE)
            else:
                display = pg.display.set_mode(size)

    return display
def getFonts():# list
	"""return a list with pygame fonts."""
	return pygame.font.get_fonts()
def getFrames(image, framesize):# list
    """
    return a list of frames clipped from an image.
    'framesize' must be a tuple of 2.
    usage:
    frames = getFrames(spritesheet, (16, 16)).
    """
    frames = []

    rows = int(image.get_rect().height / framesize[1])
    cells = int(image.get_rect().width / framesize[0])
    rect = pg.Rect((0, 0), framesize)

    # running each frame
    for row in range(rows):
        y = row * framesize[1]
        rect.top = y
        for cell in range(cells):
            x = cell * framesize[0]
            rect.left = x

            image.set_clip(rect)
            clip = image.subsurface(image.get_clip())

            frames.append(clip)
    del(clip, rect)

    return frames
def getMouse():# tuple
    """returns pygame.mouse position."""
    return pg.mouse.get_pos()
def listAttributes(object):
    """pretty-prints all available object-attributes."""
    prettyPrint(object.__dict__.keys())
def makeText(**kwargs):
    """returns a pg.surface with the text already blitten to it."""
    default = {
        "text": "No Text was passed.",
        "font": "ebrima",
        "size": 16,
        "color": (255, 255, 255),
        "background": None,
        "antialias": True,
        "bold": False,
        "italic": False,
        "wrap": None
    }
    # validating arguments
    cfg = validateDict(kwargs, default)
    # building font-object
    font = pg.font.SysFont(cfg["font"], cfg["size"])
    font.set_bold(cfg["bold"])
    font.set_italic(cfg["italic"])
    # normal render for none-wrapping content
    if not cfg["wrap"]:
        text = font.render(
            cfg["text"],
            cfg["antialias"],
            cfg["color"]
        )
    # wrapping text
    else:
        text = wrapText(
            font = font,
            text = cfg["text"],
            size = cfg["wrap"],
            color = cfg["color"],
            antialias = cfg["antialias"]
        )
    # drawing background if one is given
    surface = pg.Surface((text.get_rect().size), pg.SRCALPHA)
    if cfg["background"]: surface.fill(cfg["background"])
    surface.blit(text, (0, 0))

    return surface
def repeatBG(image, size, axis="xy", pos=(0, 0)):# pg.surface
    """
    returns a pygame surface where the given image will be drawn repeatedly.
    'axis':
        'x' repeat the image along the horizontal line.
        'y' repeat the image along the vertival line.
        'xy': fill the whole surface with one image repeated right and down.
    """
    # shortcut
    imagerect = image.get_rect()
    # converting size into tuple of two ints if necessary
    if type(size) == pg.Rect:
        size = size.size
    # creating a surface to draw everything on and return it
    temp = pg.Surface(size)
    # another shortcut
    temprect = temp.get_rect()
    # drawing along the given axis
    if axis == "x":
        for each in range(int(temprect.width / imagerect.width) + imagerect.width):
            temp.blit(image, (each * imagerect.width, pos[0]))
    elif axis == "y":
        for each in range(int(temprect.height / imagerect.height) + imagerect.height):
            temp.blit(image, (pos[1], each * imagerect.height))
    elif axis == "xy":
        for j in range(int(temprect.width / imagerect.width) + imagerect.width):
            for i in range(int(temprect.height / imagerect.height) + imagerect.height):
                temp.blit(image, (j * imagerect.width, i * imagerect.width))

    return temp
def scale(surface, factor):# pg.surface
    """
    scaling a surface by afactor.
    'factor' must be an integer tuple or a list.
    usage: surf = scale(display, 2).
        surf = scale(display, (100, 50))
    """
    if type(factor) is int:
        size = [each * factor for each in surface.get_rect().size]
    elif type(factor) is tuple or type(factor) is list:
        size = factor

    return pg.transform.scale(surface, size)
def wrapText(**kwargs):# pg.surface
    """returns a pygame surface. drew this function from the official pygame wiki.
        modified it a little bit.

    'text' str.
    'color' tuple of 3 ints.
    'size' an int for declaring maximal-width
    'font' a valid pygame.font-object.
    'antialias' needs to be bool.
    """
    # looking for gaps in the kwargs-dict
    if not "text" in kwargs:
        kwargs["text"] = "No Text was passed."
    if not "color" in kwargs:
        kwargs["color"] = (0, 0, 0)
    if not "antialias" in kwargs:
        kwargs["antialias"] = True
    if not "size" in kwargs:
        kwargs["size"] = 200
    if not "font" in kwargs:
        kwargs["font"] = pg.font.SysFont(# pygame.font
        	FONT["base"]["name"],
        	16
        )
    # local delarations
    font = kwargs["font"]
    text = kwargs["text"]
    color = kwargs["color"]
    aa = kwargs["antialias"]
    rect = pg.Rect(0 ,0, kwargs["size"], 500)
    y = rect.top
    lineSpacing = -2
    new_size = [kwargs["size"], 0]
    txt_surf = pg.Surface(rect.size, pg.SRCALPHA)
    # get the height of the font
    fontHeight = font.size("Tg")[1]

    while text:
        i = 1
        # declaring maximum width of line
        while font.size(text[:i])[0] < rect.width and i < len(text):
            i += 1
        # if we've wrapped the text, then adjust the wrap to the last word
        if i < len(text):
            i = text.rfind(" ", 0, i) + 1
        # render the line and blit it to the surface
        image = font.render(text[:i], aa, color)
        txt_surf.blit(image, (rect.left, y))
        y += fontHeight + lineSpacing
        new_size[1] = y
        # remove the text we just blit
        text = text[i:]

    # we want only the real text-size so we get to blit everything to a smaller
    # surface before returning it
    txt_surf2 = pg.Surface(new_size, pg.SRCALPHA)
    txt_surf2.blit(txt_surf, (0, 0))

    return txt_surf2
