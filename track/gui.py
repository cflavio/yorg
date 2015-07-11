from panda3d.core import TextNode
from direct.gui.OnscreenText import OnscreenText
from ya2.gameobject import Gui


class _Gui(Gui):
    '''This class models the GUI component of a track.'''

    def __init__(self, mdt):
        Gui.__init__(self, mdt)
        self.__debug_txt = OnscreenText(
            _('F12: toggle debug'), pos=(-.1, .1), scale=0.07, fg=(1, 1, 1, 1),
            parent=eng.a2dBottomRight, align=TextNode.ARight,
            font=eng.font_mgr.load_font('assets/fonts/zekton rg.ttf'))
        self.__wip_txt = OnscreenText(
            _('work in progress'), pos=(.1, .1), scale=0.05, fg=(1, 1, 1, 1),
            parent=eng.a2dBottomLeft, align=TextNode.ALeft,
            font=eng.font_mgr.load_font('assets/fonts/zekton rg.ttf'))
        self.__countdown_txt = OnscreenText(
            '', pos=(0, 0), scale=.2, fg=(1, 1, 1, 1),
            font=eng.font_mgr.load_font('assets/fonts/zekton rg.ttf'))
        self.__keys_txt = OnscreenText(
            _('arrows for driving; Z for braking'), pos=(.1, -.2), scale=.1,
            fg=(1, 1, 1, 1), align=TextNode.ALeft, parent=eng.a2dTopLeft,
            font=eng.font_mgr.load_font('assets/fonts/zekton rg.ttf'))
        self.countdown_cnt = 3
        taskMgr.doMethodLater(1.0, self.process_countdown, 'coutdown')

    def process_countdown(self, task):
        if self.countdown_cnt >= 0:
            self.mdt.audio.countdown_sfx.play()
            txt = str(self.countdown_cnt) if self.countdown_cnt else _('GO!')
            self.__countdown_txt.setText(txt)
            self.countdown_cnt -= 1
            return task.again
        else:
            self.__countdown_txt.destroy()
            destroy_keys = lambda task: self.__keys_txt.destroy()
            taskMgr.doMethodLater(5.0, destroy_keys, 'destroy keys')
            game.track.fsm.demand('Race')

    def destroy(self):
        Gui.destroy(self)
        self.__debug_txt.destroy()
        self.__wip_txt.destroy()
