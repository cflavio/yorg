from direct.gui.DirectButton import DirectButton
from direct.gui.DirectGuiGlobals import DISABLED, NORMAL
from yyagl.engine.gui.page import Page, PageGui
from yyagl.racing.season.season import SingleRaceSeason
from yyagl.engine.gui.imgbtn import ImageButton
from .netmsgs import NetMsgs


class DriverPageGui(PageGui):

    def __init__(self, mdt, menu):
        PageGui.__init__(self, mdt, menu)

    def build_page(self):
        menu_gui = self.menu.gui
        self.track_path = 'tracks/' + self.menu.track
        self.widgets += [
            ImageButton(
                scale=.4, pos=(-1.2 + i * .6, 1, .1), frameColor=(0, 0, 0, 0),
                image='assets/images/drivers/driver%s.png' % i,
                command=game.fsm.demand,
                extraArgs=['Race', self.mdt.track, self.mdt.car, [], str(i)],
                **self.menu.gui.imgbtn_args)
            for i in range(1, 4)]
        PageGui.build_page(self)


class DriverPage(Page):
    gui_cls = DriverPageGui

    def __init__(self, menu, track, car):
        self.track = track
        self.car = car
        Page.__init__(self, menu)
