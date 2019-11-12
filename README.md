# t_pygo

implementation example:

```python
# dependencies
import t_pygo as go
import pygame as pg

# assignments
app = go.Window({
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
	"background": (0, 0, 0),
	"size": camera.rect.size,
	"opacity": 200
})
pause_button_continue = go.Button({
	"size": (160, 50),
	"background": (75, 75, 75),
	"textcolor": (200, 200, 200),
	"text": "Continue",
	"fontsize": 22,
	"bold": True,
	#"position": camera.anchors["midcenter"]
	"position": (camera.anchors["middle"], 160)
})
pause_button_exit = go.Button({
	"size": (160, 50),
	"background": (75, 75, 75),
	"textcolor": (200, 200, 200),
	"text": "Exit Game",
	"fontsize": 22,
	"bold": True,
	#"position": camera.anchors["midcenter"]
	"position": (camera.anchors["middle"], 240)
})

# functions
def setup():
	"""pre-setup for the game before entering the main-loop."""
	# resizing app relative to camera size
	app.resize(camera.rect.size)
	# player has to know the active maps blocking elements
	player.knownblocks = map.blocks
	# placing player on the map
	if map.playerstart:
	    player.position(map.playerstart)
def main():
	"""main loop."""
	while True:
		# --------------------------- events ---------------------------- #
		events = app.events()
		# ESCAPE KEY
		if app.keys()["esc"]:
			app.pause()
		# MOUSE WHEEL
		if app.mouseWheel() == "up":
			print("mouse wheel up")
		elif app.mouseWheel() == "down":
			print("mouse wheel down")
		# PAUSE MENU
		if app.paused:
			if pause_button_continue.leftClick(events):
				app.pause()
			elif pause_button_exit.leftClick(events):
				app.quit()
		# ------------------------ game routines ------------------------ #
		# try to move the player
		if not app.paused:
			player.move()
		# --------------------------- drawing --------------------------- #
		# drawing everything to the camera
		camera.draw((0, 0, 0))
		camera.draw(map.preview, camera.rect)
		camera.draw(player, "center")
		camera.draw(
			go.drawBorder(camera, camera.rect, (3, 'solid', (255, 0, 0)))
		)
		camera.draw(text)
		# finally drawing camera to app
		app.draw(camera)
		# drawing gui when paused
		if app.paused:
			app.draw(pause_background)
			app.draw(pause_button_continue, pause_button_continue.rect)
			app.draw(pause_button_exit, pause_button_exit.rect)
		# -------------------------- updating --------------------------- #
		# frames per second
		text.update({
			"text": "quacks: {0}".format(app.fps)
		})
		# camera recalculatings
		camera.update()
		# pygames display updates
		app.update()
# begin game-routines
if __name__ == '__main__':
    setup()
    main()

```
