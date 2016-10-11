from direct.gui.DirectButton import DirectButton
from racing.game.engine.gui.mainpage import MainPage, MainPageGui
from racing.game.engine.gui.page import Page, PageEvent, PageGui
from carpage import CarPage
from trackpage import TrackPage


class SingleplayerPageGui(PageGui):

    def build(self):
        menu_gui = self.menu.gui
        menu_args = self.menu.gui.menu_args
        game.ranking = None
        def on_continue():
            game.ranking = game.options['last_ranking']
            game.fsm.demand('Loading')
        def on_tournament():
            game.ranking = {'kronos': 0, 'themis': 0, 'diones': 0}
            self.menu.track = 'prototype'
            self.menu.logic.push_page(CarPage(self.menu))
        menu_data = [
            ('Single race', lambda: self.menu.logic.push_page(TrackPage(self.menu))),
            ('New tournament', on_tournament),
            ('Continue tournament', on_continue)]
        self.widgets += [
            DirectButton(
                text=menu[0], scale=.2, pos=(0, 1, .4-i*.28),
                text_fg=(.75, .75, .75, 1),
                text_font=menu_gui.font, frameColor=menu_args.btn_color,
                command=menu[1], frameSize=menu_args.btn_size,
                rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
                clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))
            for i, menu in enumerate(menu_data)]
        if 'last_ranking' not in game.options.dct:
            self.widgets[-1]['state'] = DISABLED
            self.widgets[-1].setAlphaScale(.25)
        PageGui.build(self)


class SingleplayerPage(Page):
    '''This class models a page.'''
    gui_cls = SingleplayerPageGui
