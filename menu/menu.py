from sys import exit
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectCheckButton import DirectCheckButton
from direct.gui.DirectGuiGlobals import FLAT, DISABLED, NORMAL
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectOptionMenu import DirectOptionMenu
from direct.gui.DirectSlider import DirectSlider
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectDialog import OkDialog
from direct.gui.DirectGui import DirectEntry
from panda3d.core import TextNode
from racing.game.gameobject.gameobject import Fsm, GameObjectMdt, Gui
from racing.game.engine.gui.page import Page, PageEvent, PageGui
from racing.game.engine.gui.mainpage import MainPage, MainPageGui
from racing.game.engine.gui.menu import MenuArgs, Menu
from racing.game.engine.lang import LangMgr
from racing.game.dictfile import DictFile
from racing.game.engine.network.server import Server
from racing.game.engine.network.client import Client, ClientError
from mainpage import YorgMainPage


class _Gui(Gui):
    """ Definition of the MenuGui Class """

    def __init__(self, mdt):
        Gui.__init__(self, mdt)
        menu_args = MenuArgs(
            'assets/fonts/zekton rg.ttf', (.75, .75, .75, 1), .12,
            (-3, 3, -.32, .88), (0, 0, 0, .2), (.9, .9, .9, .8),
            'assets/images/gui/menu_background.jpg',
            'assets/sfx/menu_over.wav', 'assets/sfx/menu_clicked.ogg',
            'assets/images/icons/%s_png.png')
        self.menu = Menu(menu_args)
        self.menu.logic.push_page(YorgMainPage(self.menu))

    def destroy(self):
        Gui.destroy(self)
        self.menu = self.menu.destroy()


class YorgMenu(GameObjectMdt):
    gui_cls = _Gui
