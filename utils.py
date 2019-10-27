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
    "tiles": os.getcwd() + "\\assets\\tiles",
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

def prettyPrint(data, sort=False, tabs=4):
    """pretty-print dicts."""
    if data.__class__ is dict:
        print(json.dumps(data, sort_keys=sort, indent=tabs))
    else:
        print("Nothing to pretty-print.")
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
        # draw object in the center
        if position == "center":
            try:
                osize = object.get_rect().size
            except AttributeError:
                osize = object.image.get_rect().size
            dsize = destination.get_rect().size

            x = int(dsize[0] / 2) - int(osize[0] / 2)
            y = int(dsize[1] / 2) - int(osize[1] / 2)
            position = (x, y)

    # drawing depending on object's type
    if type(object) is tuple:
        destination.fill(
            object, destination.get_rect(),
            special_flags=blendmode
            )
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

    # recursively drawing objects from a list
    elif type(object) is list:
        for each in object:
            draw(each, destination, position, blendmode=blendmode)

    return destination
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
def validateDict(config={}, defaults={}):# dict
    """validate a dictionary by given defaults. params must be dict."""
    validated = {}

    for each in defaults:
        try:
            validated[each] = config[each]
        except KeyError:
            validated[each] = defaults[each]

    return validated
def getFrames(image, framesize):# list
    """
    return a list of frames clipped from an image.
    'framesize' must be a tuple of 2.
    usage: frames = getFrames(spritesheet, (16, 16)).
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
