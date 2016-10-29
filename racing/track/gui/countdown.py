from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage


class Countdown(object):

    def __init__(self, mdt):
        self.mdt = mdt
        self.__countdown_txt = OnscreenText(
            '', pos=(0, 0), scale=.2, fg=(1, 1, 1, 1),
            font=eng.font_mgr.load_font('assets/fonts/zekton rg.ttf'))
        self.countdown_cnt = 3
        self.__keys_img = OnscreenImage(
            image='assets/images/gui/keys.png', parent=eng.base.a2dTopLeft,
            pos=(.7, 1, -.4), scale=(.6, 1, .3))
        self.__keys_img.setTransparency(True)
        taskMgr.doMethodLater(1.0, self.process_countdown, 'coutdown')

    def process_countdown(self, task):
        if self.countdown_cnt >= 0:
            self.mdt.audio.countdown_sfx.play()
            txt = str(self.countdown_cnt) if self.countdown_cnt else _('GO!')
            self.__countdown_txt.setText(txt)
            self.countdown_cnt -= 1
            return task.again
        self.__countdown_txt.destroy()
        destroy_keys = lambda task: self.__keys_img.destroy()
        taskMgr.doMethodLater(5.0, destroy_keys, 'destroy keys')
        self.mdt.fsm.demand('Race')

    def destroy(self):
        pass
