from itertools import product
from direct.gui.OnscreenText import OnscreenText
from yyagl.engine.gui.page import Page, PageFacade
from yyagl.engine.gui.imgbtn import ImgBtn
from yyagl.gameobject import GameObject
from .netmsgs import NetMsgs
from .thankspage import ThanksPageGui


class TrackPageGui(ThanksPageGui):

    def __init__(self, mdt, trackpage_props):
        self.props = trackpage_props
        ThanksPageGui.__init__(self, mdt, trackpage_props.gameprops.menu_args)

    def bld_page(self):
        txt = OnscreenText(text=_('Select the track'), pos=(-.2, .8),
                           **self.menu_args.text_args)
        self.add_widget(txt)
        t_a = self.menu_args.text_args.copy()
        t_a['scale'] = .06
        tracks_per_row = 3
        gprops = self.props.gameprops
        for row, col in product(range(2), range(tracks_per_row)):
            if row * tracks_per_row + col >= len(gprops.season_tracks):
                break
            z_offset = 0 if len(gprops.season_tracks) > tracks_per_row else .35
            num_tracks = len(gprops.season_tracks) - tracks_per_row \
                if row == 1 else min(tracks_per_row, len(gprops.season_tracks))
            x_offset = .3 * (tracks_per_row - num_tracks)
            btn = ImgBtn(
                scale=.3,
                pos=(-.8 + col * .6 + x_offset, 1, .4 - z_offset - row * .7),
                frameColor=(0, 0, 0, 0),
                image=gprops.track_img % gprops.season_tracks[
                    col + row * tracks_per_row],
                command=self.on_track, extraArgs=[gprops.season_tracks[
                    col + row * tracks_per_row]],
                **self.menu_args.imgbtn_args)
            txt = OnscreenText(
                gprops.tracks_tr()[col + row * tracks_per_row],
                pos=(-.8 + col * .6 + x_offset, .14 - z_offset - row * .7),
                **t_a)
            map(self.add_widget, [btn, txt])
        ThanksPageGui.bld_page(self)

    def on_track(self, track):
        self.eng.log('selected ' + track)
        self.notify('on_track_selected', track)
        self.notify('on_push_page', 'car_page', [self.props])


class TrackPageGuiServer(TrackPageGui):

    def on_track(self, track):
        self.notify('on_track_selected', track)
        self.notify('on_push_page', 'carpageserver', [self.props])
        self.eng.server.send([NetMsgs.track_selected, track])


class TrackPage(Page):
    gui_cls = TrackPageGui

    def __init__(self, trackpage_props):
        init_lst = [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [self, trackpage_props])]]
        GameObject.__init__(self, init_lst)
        PageFacade.__init__(self)
        # invoke Page's __init__

    def destroy(self):
        GameObject.destroy(self)
        PageFacade.destroy(self)


class TrackPageServer(TrackPage):
    gui_cls = TrackPageGuiServer
