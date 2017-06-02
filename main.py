from panda3d.core import WindowProperties

wp = WindowProperties()
wp.set_size(800, 600)
wp.set_fixed_size(True)
wp.set_undecorated(True)
wp.set_title('Galaxis')
wp.set_icon_filename('data/launcher/icon/icon.ico')

from src.core.showbase import *

from src.menu.launcher import Launcher

base.disableMouse()
base.openDefaultWindow(props = wp)
base.setBackgroundColor(0, 0, 0)

Launcher()
base.run()