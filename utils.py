# dependencies
import json, os, ctypes
import pygame as pg

# project and library pathes
PATH = {
    "go": os.path.dirname(__file__),
    "sysimg": os.path.dirname(__file__) + "\\images",
    "root": os.getcwd(),
    "assets": os.getcwd() + "\\assets",
    "images": os.getcwd() + "\\assets\\images",
    "maps": os.getcwd() + "\\assets\\maps",
    "tilesets": os.getcwd() + "\\assets\\tilesets",
    "entities": os.getcwd() + "\\assets\\entities"
}
LIBPATH = {
    "noimage": PATH["sysimg"] + "\\noimage.png",
    "notile": PATH["sysimg"] + "\\notile.png",
    "windowbg": PATH["sysimg"] + "\\bg01.png",
    "windowicon": PATH["sysimg"] + "\\ente.png"
}
RESOLUTIONS = {
    "1920x1080": (1920, 1080),
    "800x400": (800, 400)
}

# console
def prettyPrint(data, sort=False, tabs=4):
    """pretty-print dicts."""
    if data.__class__ is dict:
        print(json.dumps(data, sort_keys=sort, indent=tabs))
    else:
        print("Nothing to pretty-print.")
# files & directories
def loadAssets(path):# list
    """
    walk the assets-directory and open each json file. plus appending file name
    and file path to the json file.
    """
    list = []

    for dirs in os.walk(path):
        for each in dirs[2]:
            if each.split(".")[1] == "json":
                config = loadJSON(dirs[0] + "\\" + each)
                config.update({"filename": each})
                list.append(config)
            # if directory has an image
            elif each.split(".")[1] == "png":
                config = {
                    "name": each.split(".")[0],
                    "filename": each,
                    "type": "image",
                    "filepath": dirs[0]
                }

                list.append(config)

    return list
def loadJSON(path):# dict
    """load and convert a JSON file to a dict."""
    with open(path) as text:
        content = "".join(text.readlines())
        js = json.loads(content)
        js.update({"name": path.split("\\")[-2]})
        js.update({"path": path})
        # //TODO tidy up
        s = path.split("\\")
        s = os.path.join(*s, "\\", *s[1:-1])
        js.update({"filepath": s})
        js.update({"filename": path.split("\\")[-1]})

    return js
# dictionary operations
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
# pygame
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
def draw(object, destination, position=(0, 0), blendmode=0):# pygame.surface
    """
    drawing a single or multiple objects to the destination surface. then
    return itself. 'position' can be tuple, pygame rect or a string.
    'special_flags' is for optional surface blending on each other.
    usage:
    draw(
        player,
        display,
        pygame.Rect(0, 0, 160, 120),
        special_flags=pygame.BLEND_ADD
    )
    """
    if type(position) is str:
        # draw object in the relative to the given string
        if position == "center":
            try:
                osize = object.get_rect().size
            except AttributeError:
                osize = object.image.get_rect().size
            dsize = destination.get_rect().size

            x = int(dsize[0] / 2) - int(osize[0] / 2)
            y = int(dsize[1] / 2) - int(osize[1] / 2)
            position = (x, y)
    # recursively drawing depending on object's type by calling this function
    # again
    if type(object) is tuple:
        destination.fill(
            object, destination.get_rect(),
            special_flags=blendmode
        )
    elif type(object) is list:
        for each in object:
            draw(each, destination, position, blendmode=blendmode)
    elif type(object) is dict:
        for each in object:
            destination.blit(object[each], position)
    elif object.__class__.__bases__[0] is pg.Surface or type(object) is pg.Surface:
        destination.blit(object, position, special_flags=blendmode)
    elif object.__class__.__bases__[0] is pg.sprite.Sprite:
        destination.blit(object.image, position, special_flags=blendmode)
    elif object.__class__ is pg.sprite.Group:
        for sprite in object:
            destination.blit(
                sprite.image,
                sprite.rect.topleft,
                special_flags=blendmode
            )
    # might puke out an error on giving anything else than pg.sprite.Sprite
    else:
        destination.blit(object.image, position)
    return destination
def drawBorder(surface, rect, border):# pygame surface
    """
    drawing a border to the given surface and return it.
    syntax for border is (BorderSize<Int>, LineStyle<Str>, Color<Tuple>).
    example: config = (1, 'solid', (255, 255, 255)).
    usage: surf = drawBorder(display, (0, 0, 16, 16), (1, 'solid', (0, 0, 0))).
    """
    size, line, color = border

    pg.draw.lines(
        surface,
        color,
        False,
        [
            (0, 0),
            (0, rect.height - 1),
            (rect.width - 1, rect.height - 1),
            (rect.width - 1, 0),
            (0, 0)
        ],
        size
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
        "topleft": (0 , 0),
        "topcenter": (int(room[0] / 2) , 0),
        "topright": (room[0] , 0),
        "midleft": (0 , int(room[1] / 2)),
        "midcenter": (int(room[0] / 2) , int(room[1] / 2)),
        "midright": (room[0] , int(room[1] / 2)),
        "bottomleft": (0 , room[1]),
        "bottomcenter": (int(room[0] / 2) , room[1]),
        "bottomright": (room[0] , room[1])
    }
    return anchors
def getDisplay(size, **kwargs):# pygame.display.surface
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
	"""return a list with pygame-fonts."""
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
def scale(surface, factor):# pygame.surface
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
def wrapText(text, color, rect, font, aa=False, bkg=None):# pygame.surface
    """
    returns a pygame surface. drew this function from the official pygame wiki.
        modified it a little bit.
    'text' a text 'string'.
    'color' tuple of 3 ints.
    'rect' a valid pygame.rect.
    'font' a valid pygame.font object.
    'aa' antialias needs to be bool.
    'bkg' background.
    """
    y = rect.top
    lineSpacing = -2
    txt_surf = pg.Surface(rect.size, pg.SRCALPHA)
    # get the height of the font
    fontHeight = font.size("Tg")[1]
    while text:
        i = 1
        # determine if the row of text will be outside our area
        if y + fontHeight > rect.bottom:
            break
        # determine maximum width of line
        while font.size(text[:i])[0] < rect.width and i < len(text):
            i += 1
        # if we've wrapped the text, then adjust the wrap to the last word
        if i < len(text):
            i = text.rfind(" ", 0, i) + 1
        # render the line and blit it to the surface
        if bkg:
            image = font.render(text[:i], 1, color, bkg)
            image.set_colorkey(bkg)
        else:
            image = font.render(text[:i], aa, color)
        txt_surf.blit(image, (rect.left, y))
        y += fontHeight + lineSpacing
        # remove the text we just blitted
        text = text[i:]
    return txt_surf
