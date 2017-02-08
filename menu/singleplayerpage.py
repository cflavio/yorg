from direct.gui.DirectButton import DirectButton
from direct.gui.DirectGuiGlobals import DISABLED
from yyagl.engine.gui.page import Page, PageGui
from .carpage import CarPage
from .trackpage import TrackPage
from yyagl.racing.season.season import Season, SingleRaceSeason


class SingleplayerPageGui(PageGui):

    def build_page(self):
        menu_gui = self.menu.gui
        menu_data = [
            (_('Single race'), self.on_single_race),
            (_('New season'), self.on_start),
            (_('Continue season'), self.on_continue)]
        self.widgets += [
            DirectButton(
                text=menu[0], pos=(0, 1, .4-i*.28), command=menu[1],
                **menu_gui.btn_args)
            for i, menu in enumerate(menu_data)]
        if 'save' not in game.options.dct:
            self.widgets[-1]['state'] = DISABLED
            self.widgets[-1].setAlphaScale(.25)
        if not game.options['development']['season']:
            for idx in [-2, -1]:
                self.widgets[idx]['state'] = DISABLED
                _fg = menu_gui.btn_args['text_fg']
                _fc = self.widgets[idx]['frameColor']
                clc = lambda val: max(0, val)
                self.widgets[idx]['text_fg'] = (_fg[0] - .3, _fg[1] - .3, _fg[2] - .3, _fg[3])
                self.widgets[idx]['frameColor'] = (clc(_fc[0] - .3), clc(_fc[1] - .3), clc(_fc[2] - .3), _fc[3])
        PageGui.build_page(self)

    def on_single_race(self):
        game.logic.season = SingleRaceSeason()
        self.menu.logic.push_page(TrackPage(self.menu))

    def on_start(self):
        game.logic.season = Season()
        game.logic.season.logic.start()
        self.menu.track = 'prototype'
        self.menu.logic.push_page(CarPage(self.menu))

    def on_continue(self):
        game.logic.season = Season()
        game.logic.season.logic.load()
        game.fsm.demand('Race', 'tracks/' + game.options['save']['track'], game.options['save']['car'])

class SingleplayerPage(Page):
    gui_cls = SingleplayerPageGui
