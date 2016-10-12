'''This module provides the track page.'''
from direct.gui.DirectButton import DirectButton
from racing.game.engine.gui.page import Page, PageGui
from .carpage import CarPage
from .netmsgs import NetMsgs


class TrackPageGui(PageGui):
    '''This class defines the GUI of the track page.'''

    def build(self):
        menu_gui = self.menu.gui
        menu_args = self.menu.gui.menu_args

        def on_track(track):
            '''Called when the user clicks on a track.'''
            self.menu.track = track
            self.menu.logic.push_page(CarPage(self.menu))
            if eng.server.is_active:
                eng.server.send([NetMsgs.track_selected, track])
        menu_data = [
            ('Desert', on_track, ['desert']),
            ('Prototype', on_track, ['prototype'])]
        self.widgets += [
            DirectButton(
                text=menu[0], scale=.2, pos=(0, 1, .4-i*.28),
                text_fg=(.75, .75, .75, 1),
                text_font=menu_gui.font, frameColor=menu_args.btn_color,
                command=menu[1], extraArgs=menu[2],
                frameSize=menu_args.btn_size,
                rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
                clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))
            for i, menu in enumerate(menu_data)]
        PageGui.build(self)

    def destroy(self):
        del self.menu.track
        PageGui.destroy(self)


class TrackPage(Page):
    '''This class models a page.'''
    gui_cls = TrackPageGui
