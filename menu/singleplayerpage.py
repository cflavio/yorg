from direct.gui.DirectButton import DirectButton
from direct.gui.DirectGuiGlobals import DISABLED
from racing.game.engine.gui.page import Page, PageGui
from .carpage import CarPage
from .trackpage import TrackPage


class SingleplayerPageGui(PageGui):

    def build_page(self):
        menu_gui = self.menu.gui
        menu_args = self.menu.gui.menu_args
        game.ranking = None
        menu_data = [
            ('Single race',
             lambda: self.menu.logic.push_page(TrackPage(self.menu))),
            ('New tournament', self.on_tournament),
            ('Continue tournament', self.on_continue)]
        self.widgets += [
            DirectButton(
                text=menu[0], pos=(0, 1, .4-i*.28), command=menu[1],
                **menu_gui.btn_args)
            for i, menu in enumerate(menu_data)]
        if 'last_ranking' not in game.options.dct:
            self.widgets[-1]['state'] = DISABLED
            self.widgets[-1].setAlphaScale(.25)
        PageGui.build_page(self)

    @staticmethod
    def on_continue():
        # into tournament
        game.ranking = game.options['last_ranking']
        game.fsm.demand('Loading')

    def on_tournament(self):
        # into tournament
        game.ranking = {'kronos': 0, 'themis': 0, 'diones': 0}
        self.menu.track = 'prototype'
        self.menu.logic.push_page(CarPage(self.menu))


class SingleplayerPage(Page):
    gui_cls = SingleplayerPageGui
