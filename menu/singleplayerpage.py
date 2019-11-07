from yyagl.lib.gui import Btn
from yyagl.engine.gui.page import Page, PageFacade
from yyagl.gameobject import GameObject
from .thankspage import ThanksPageGui


class SingleplayerPageGui(ThanksPageGui):

    def __init__(self, mediator, props):
        self.props = props
        ThanksPageGui.__init__(self, mediator, props.gameprops.menu_props)

    def build(self):
        menu_data = [
            (_('Single race'), self.on_single_race),
            (_('New season'), self.on_start),
            (_('Continue season'), lambda: self.notify('on_continue'))]
        widgets = [
            Btn(
                text=menu[0], pos=(0, .4-i*.28), cmd=menu[1],
                **self.props.gameprops.menu_props.btn_args)
            for i, menu in enumerate(menu_data)]
        self.add_widgets(widgets)
        #self._set_widgets()
        ThanksPageGui.build(self)
        if not self.props.has_save:
            widgets[-1].disable()

    def on_single_race(self):
        self.notify('on_push_page', 'single_race', [self.props])

    def on_start(self):
        self.notify('on_track_selected', self.props.gameprops.season_tracks[0])
        self.notify('on_push_page', 'new_season', [self.props])


class SingleplayerPage(Page):
    gui_cls = SingleplayerPageGui

    def __init__(self, singleplayerpage_props):
        self.singleplayerpage_props = singleplayerpage_props
        Page.__init__(self, singleplayerpage_props)
        PageFacade.__init__(self)

    def _build_gui(self):
        self.gui = self.gui_cls(self, self.singleplayerpage_props)

    def destroy(self):
        Page.destroy(self)
        PageFacade.destroy(self)
