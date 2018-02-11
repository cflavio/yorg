from yyagl.library.gui import Btn
from yyagl.engine.gui.page import Page, PageFacade
from yyagl.gameobject import GameObject
from .thankspage import ThanksPageGui


class SingleplayerPageGui(ThanksPageGui):

    def __init__(self, mediator, props):
        self.props = props
        ThanksPageGui.__init__(self, mediator, props.gameprops.menu_args)

    def build(self):
        menu_data = [
            (_('Single race'), self.on_single_race),
            (_('New season'), self.on_start),
            (_('Continue season'), lambda: self.notify('on_continue'))]
        widgets = [
            Btn(
                text=menu[0], pos=(-.2, 1, .4-i*.28), command=menu[1],
                **self.props.gameprops.menu_args.btn_args)
            for i, menu in enumerate(menu_data)]
        self.add_widgets(widgets)
        self._set_widgets()
        if not self.props.has_save:
            widgets[-1].disable()
        ThanksPageGui.build(self)

    def on_single_race(self):
        self.notify('on_push_page', 'single_race', [self.props])

    def on_start(self):
        self.notify('on_track_selected', self.props.gameprops.season_tracks[0])
        self.notify('on_push_page', 'new_season', [self.props])


class SingleplayerPage(Page):
    gui_cls = SingleplayerPageGui

    def __init__(self, singleplayerpage_props):
        init_lst = [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [self, singleplayerpage_props])]]
        GameObject.__init__(self, init_lst)
        PageFacade.__init__(self)
        # invoke Page's __init__

    def destroy(self):
        GameObject.destroy(self)
        PageFacade.destroy(self)
