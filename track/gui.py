from panda3d.core import TextNode
from direct.gui.OnscreenText import OnscreenText
from ya2.gameobject import Gui


class _Gui(Gui):
    '''This class models the GUI component of a track.'''

    def __init__(self, mdt):
        Gui.__init__(self, mdt)
        self.__debug_txt = OnscreenText(
            _('F12: toggle debug'), pos=(-.1, .1), scale=0.07,
            parent=eng.a2dBottomRight, align=TextNode.ARight,
            font=eng.font_mgr.load_font('assets/fonts/zekton rg.ttf'))

    def destroy(self):
        Gui.destroy(self)
        self.__debug_txt.destroy()
