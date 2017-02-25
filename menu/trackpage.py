from yyagl.engine.gui.page import Page, PageGui
from .carpage import CarPage, CarPageServer
from yyagl.engine.gui.imgbtn import ImageButton
from .netmsgs import NetMsgs
from direct.gui.OnscreenText import OnscreenText
from random import shuffle


class TrackPageGui(PageGui):

    def build_page(self):
        menu_gui = self.menu.gui

        txt = OnscreenText(text=_('Select the track'), pos=(0, .8),
                           **menu_gui.text_args)
        self.widgets += [txt]

        tracks = ['desert', 'mountain']
        track_names = [_('desert'), _('mountain')]
        names = open('assets/thanks.txt').readlines()
        shuffle(names)
        names = names[:2]
        t_a = self.menu.gui.text_args.copy()
        del t_a['scale']
        for i in range(len(tracks)):
            img = ImageButton(
                scale=.5, pos=(-.5 + i * 1.0, 1, .1), frameColor=(0, 0, 0, 0),
                image='assets/images/tracks/%s.png' % tracks[i],
                command=self.on_track, extraArgs=[tracks[i]],
                **self.menu.gui.imgbtn_args)
            txt = OnscreenText(track_names[i], pos=(-.5 + i * 1.0, .45),
                               scale=.08, **t_a)
            thanks = OnscreenText(_('thanks to:'), pos=(-.5 + i * 1.0, -.2),
                                  scale=.06, **t_a)
            name = OnscreenText(names[i], pos=(-.5 + i * 1.0, -.3), scale=.08,
                                **t_a)
            self.widgets += [img, txt, thanks, name]
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
