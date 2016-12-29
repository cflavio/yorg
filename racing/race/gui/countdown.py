from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from racing.game.observer import Subject


class Countdown(Subject):

    def __init__(self):
        Subject.__init__(self)
        self.countdown_sfx = loader.loadSfx('assets/sfx/countdown.ogg')
        self.__countdown_txt = OnscreenText(
            '', pos=(0, 0), scale=.2, fg=(1, 1, 1, 1),
            font=eng.font_mgr.load_font('assets/fonts/zekton rg.ttf'))
        self.countdown_cnt = 3
        taskMgr.doMethodLater(1.0, self.process_countdown, 'coutdown')

    def process_countdown(self, task):
        if self.countdown_cnt >= 0:
            self.countdown_sfx.play()
            txt = str(self.countdown_cnt) if self.countdown_cnt else _('GO!')
            self.__countdown_txt.setText(txt)
            self.countdown_cnt -= 1
            return task.again
        self.__countdown_txt.destroy()
        self.notify('on_start_race')
