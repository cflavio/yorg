from yyagl.racing.race.race import Race, RaceSinglePlayer, RaceServer, \
    RaceClient
from yyagl.gameobject import Fsm
from yyagl.engine.gui.page import PageGui
from menu.menu import YorgMenu
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectButton import DirectButton
import sys
from direct.gui.DirectGuiGlobals import FLAT
from direct.gui.DirectFrame import DirectFrame


class _Fsm(Fsm):

    def __init__(self, mdt):
        Fsm.__init__(self, mdt)
        self.defaultTransitions = {
            'Menu': ['Race', 'Exit'],
            'Race': ['Ranking', 'Menu', 'Exit'],
            'Ranking': ['Tuning', 'Exit'],
            'Tuning': ['Menu', 'Race', 'Exit'],
            'Exit': ['Exit']}
        self.load_txt = None
        self.preview = None
        self.cam_tsk = None
        self.cam_node = None
        self.ranking_texts = None
        self.send_tsk = None
        self.cam_pivot = None
        self.ready_clients = None
        self.curr_load_txt = None
        self.__menu = None
        self.race = None

    def enterMenu(self):
        eng.log_mgr.log('entering Menu state')
        self.__menu = YorgMenu()
        self.mdt.audio.menu_music.play()

    def exitMenu(self):
        eng.log_mgr.log('exiting Menu state')
        self.__menu.destroy()
        self.mdt.audio.menu_music.stop()

    def enterRace(self, track_path='', car_path='', player_cars=[], driver=''):
        eng.log_mgr.log('entering Race state')
        if eng.server.is_active:
            self.race = RaceServer()
        elif eng.client.is_active:
            self.race = RaceClient()
        else:
            self.race = RaceSinglePlayer()
        eng.log_mgr.log('selected driver: ' + driver)
        self.race.fsm.demand('Loading', track_path, car_path, player_cars)

    def exitRace(self):
        eng.log_mgr.log('exiting Race state')
        self.race.destroy()

    def enterRanking(self):
        game.logic.season.logic.ranking.gui.show()

    def exitRanking(self):
        game.logic.season.logic.ranking.gui.hide()

    def enterTuning(self):
        game.logic.season.logic.tuning.gui.show()

    def exitTuning(self):
        game.logic.season.logic.tuning.gui.hide()

    def enterExit(self):
        self.frm = DirectFrame(frameSize=(-1.5, 1.5, -.9, .9), frameColor=(1, 1, 1, .85))
        menu_gui = self.__menu.gui.menu
        txt = _(
            'Please, visit our site! We hope you can find interesting stuff there. '
            'Moreover, by visiting it (especially disabling your adblocker onto the site) '
            'you support us and contribute to keep Yorg as free as possible. Thank you very much! :)')
        self.txt = OnscreenText(text=txt, pos=(0, .8), scale=.08, wordwrap=32,
            fg=(1, 1, 1, 1), font=eng.font_mgr.load_font('assets/fonts/zekton rg.ttf'))
        menu_data = [
            ('Visit and exit', _('visit our site and exit\n(I love to support you!)'),
             lambda: self.on_end(True)),
            ('Only exit', _("exit without visiting our site\n(I don't want to support you)"),
             lambda: self.on_end(False))]
        self.widgets = []
        btn_args = {
            'text_font': eng.font_mgr.load_font('assets/fonts/zekton rg.ttf'),
            'text_fg': (.75, .75, .75, 1),
            'frameColor': (0, 0, 0, .2),
            'relief': FLAT,
            'frameSize': (-1, 1, -.2, .16),
            'rolloverSound': loader.loadSfx('assets/sfx/menu_over.wav'),
            'clickSound': loader.loadSfx('assets/sfx/menu_clicked.ogg')}
        self.widgets += [DirectButton(text=menu_data[0][1], pos=(0, 1, 0), command=menu_data[0][2], text_scale=.12, **btn_args)]
        self.widgets += [DirectButton(text=menu_data[1][1], pos=(0, 1, -.5), command=menu_data[1][2], text_scale=.08, **btn_args)]
        for i, wdg in enumerate(self.widgets):
            PageGui.transl_text(wdg, menu_data[i][0])

    def on_end(self, visit):
        if visit:
            eng.gui.open_browser('http://www.ya2.it')
        sys.exit()

    def exitExit(self):
        for wdg in [self.txt, self.frm] + self.widgets:
            wdg.destroy()
