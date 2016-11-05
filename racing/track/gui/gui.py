from panda3d.core import TextNode
from direct.gui.OnscreenText import OnscreenText
from racing.game.gameobject import Gui
from .minimap import Minimap


class TrackGui(Gui):

    def __init__(self, mdt, track):
        Gui.__init__(self, mdt)
        self.track = track
        self.debug_txt = OnscreenText(
            '', pos=(-.1, .1), scale=0.05, fg=(1, 1, 1, 1),
            parent=eng.base.a2dBottomRight, align=TextNode.ARight)
        self.way_txt = OnscreenText(
            '', pos=(.1, .4), scale=0.1, fg=(1, 1, 1, 1),
            parent=eng.base.a2dBottomLeft, align=TextNode.ALeft,
            font=eng.font_mgr.load_font('assets/fonts/zekton rg.ttf'))
        self.minimap = Minimap(track, self.mdt.phys.lrtb)

    def destroy(self):
        Gui.destroy(self)
        self.way_txt.destroy()
        self.minimap.destroy()
