from logging import info
from itertools import product
from yyagl.lib.gui import Text
from yyagl.engine.gui.page import Page, PageFacade
from yyagl.engine.gui.imgbtn import ImgBtn
from yyagl.gameobject import GameObject
from .netmsgs import NetMsgs
from .thankspage import ThanksPageGui


class TrackPageGui(ThanksPageGui):

    def __init__(self, mediator, trackpage_props, room):
        self.props = trackpage_props
        self.room = room
        ThanksPageGui.__init__(self, mediator, trackpage_props.gameprops.menu_props)

    def build(self):
        txt = Text(_('Select the track'), pos=(0, .8),
                           **self.menu_props.text_args)
        self.add_widgets([txt])
        t_a = self.menu_props.text_args.copy()
        t_a['scale'] = .06
        tracks_per_row = 4
        gprops = self.props.gameprops
        for row, col in product(range(2), range(tracks_per_row)):
            if row * tracks_per_row + col >= len(gprops.season_tracks):
                break
            z_offset = 0 if len(gprops.season_tracks) > tracks_per_row else .35
            num_tracks = len(gprops.season_tracks) - tracks_per_row \
                if row == 1 else min(tracks_per_row, len(gprops.season_tracks))
            x_offset = .3 * (tracks_per_row - num_tracks)
            btn = ImgBtn(
                scale=(.3, .3),
                pos=(-.9 + col * .6 + x_offset, .4 - z_offset - row * .7),
                frame_col=(0, 0, 0, 0),
                img=gprops.track_img % gprops.season_tracks[
                    col + row * tracks_per_row],
                cmd=self.on_track, extra_args=[gprops.season_tracks[
                    col + row * tracks_per_row]],
                **self.menu_props.imgbtn_args)
            txt = Text(
                gprops.tracks_tr()[col + row * tracks_per_row],
                pos=(-.9 + col * .6 + x_offset, .14 - z_offset - row * .7),
                **t_a)
            self.add_widgets([btn, txt])
        ThanksPageGui.build(self, exit_behav=self.eng.server.is_active)

    def on_track(self, track):
        info('selected ' + track)
        self.notify('on_track_selected', track)
        self.notify('on_push_page', 'car_page', [self.props])


class TrackPageServerGui(TrackPageGui):

    def on_track(self, track):
        self.notify('on_track_selected', track)
        self.notify('on_push_page', 'carpageserver', [self.props])
        self.eng.client.send(['track_selected', track, self.room])

    def _on_quit(self):
        self.eng.server.stop()
        self.eng.client.is_server_active = False
        self.eng.client.is_client_active = False
        self.eng.client.register_rpc('leave_room')
        self.eng.client.leave_room(self.room)
        TrackPageGui._on_quit(self)


class TrackPageLocalMPGui(TrackPageGui):

    def on_track(self, track):
        self.notify('on_track_selected_lmp', track)
        self.notify('on_push_page', 'carpagelocalmp', [self.props])


class TrackPage(Page):
    gui_cls = TrackPageGui

    def __init__(self, trackpage_props, room=None):
        self.trackpage_props = trackpage_props
        self.room = room
        Page.__init__(self, trackpage_props)
        PageFacade.__init__(self)

    @property
    def init_lst(self): return [
        [('event', self.event_cls, [self])],
        [('gui', self.gui_cls, [self, self.trackpage_props, self.room])]]

    def destroy(self):
        Page.destroy(self)
        PageFacade.destroy(self)


class TrackPageServer(TrackPage):
    gui_cls = TrackPageServerGui


class TrackPageLocalMP(TrackPage):
    gui_cls = TrackPageLocalMPGui
