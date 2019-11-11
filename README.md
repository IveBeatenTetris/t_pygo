# t_pygo

```python
# dependencies
import t_pygo as go
import pygame as pg

# assignments
window = go.Window({
	"title": "merely something 0.0.1",
	"zoom": 1,
	"fps": 70
})
map = go.Map("test1")
player = go.Player("p1")
camera = go.Camera({
	"size": (640, 480),
	"tracking": player
})
text = go.Text({
	"font": "Verdana",
	"size": 20,
	"text": "fps",
	"color": (255, 255, 255)
})

# gui
pause_background = go.Overlay({
	"background": (20, 40, 60),
	"size": camera.rect.size,
	"opacity": 175
})
pause_back_button = go.Button({
	"size": (140, 50),
	"background": (75, 75, 75),
	"text": "Back",
	"position": camera.anchors["midcenter"]
})

# functions
def setup():
	"""pre-setup for the game before entering the main-loop."""
	window.resize(camera.rect.size)
	player.knownblocks = map.blocks
	if map.playerstart:
	    player.position(map.playerstart)
def main():
	"""main loop."""
	while True:
		# --------------------------- events ---------------------------- #
		window.getEvents()
		# ------------------------ game routines ------------------------ #
		# try to move the player
		if not window.pausemenu:
			player.move()
		# --------------------------- drawing --------------------------- #
		# drawing everything to the camera
		camera.draw((0, 0, 0))
		#camera.draw(map.layers, camera.rect)
		camera.draw(map.preview, camera.rect)
		camera.draw(player, "center")
		camera.draw(
			go.drawBorder(camera, camera.rect, (3, 'solid', (255, 0, 0)))
		)
		camera.draw(text)
		# finally drawing camera to window
		window.draw(camera)
		# drawing gui when paused
		if window.pausemenu:
			window.draw(pause_background)
			window.draw(pause_back_button, pause_back_button.rect)
		# -------------------------- updating --------------------------- #
		# frames per second
		text.update({
			"text": "quacks: {0}".format(window.fps)
		})
		# camera recalculatings
		camera.update()
		# pygames display updates
		window.update()
# begin game-routines
if __name__ == '__main__':
    setup()
    main()
```
