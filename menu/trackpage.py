from direct.gui.DirectButton import DirectButton
from yyagl.engine.gui.page import Page, PageGui
from .carpage import CarPage, CarPageServer
from yyagl.engine.gui.imgbtn import ImageButton
from .netmsgs import NetMsgs
from direct.gui.OnscreenText import OnscreenText


class TrackPageGui(PageGui):

    def build_page(self):
        menu_gui = self.menu.gui

        txt = OnscreenText(text=_('Select the track'), pos=(0, .8), **menu_gui.text_args)
        self.widgets += [txt]

        menu_data = ['desert', 'prototype']
        self.widgets += [
            ImageButton(
                scale=.5, pos=(-.5 + i * 1.0, 1, .1), frameColor=(0, 0, 0, 0),
                image='assets/images/tracks/%s.png' % menu,
                command=self.on_track, extraArgs=[menu],
                **self.menu.gui.imgbtn_args)
            for i, menu in enumerate(menu_data)]
        PageGui.build_page(self)

    def on_track(self, track):
        self.menu.track = track
        self.menu.logic.push_page(CarPage(self.menu))

    def destroy(self):
        if hasattr(self.menu, 'track'):
            del self.menu.track
        PageGui.destroy(self)


class TrackPageGuiServer(TrackPageGui):

    def on_track(self, track):
        self.menu.track = track
        self.menu.logic.push_page(CarPageServer(self.menu))
        eng.server.send([NetMsgs.track_selected, track])


class TrackPage(Page):
    gui_cls = TrackPageGui


class TrackPageServer(Page):
    gui_cls = TrackPageGuiServer
