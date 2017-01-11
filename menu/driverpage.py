from direct.gui.DirectButton import DirectButton
from direct.gui.DirectGuiGlobals import DISABLED, NORMAL
from yyagl.engine.gui.page import Page, PageGui
from yyagl.racing.season.season import SingleRaceSeason
from yyagl.engine.gui.imgbtn import ImageButton
from .netmsgs import NetMsgs
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import TextureStage


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
                command=self.on_click, extraArgs=[i],
                **self.menu.gui.imgbtn_args)
            for i in range(1, 4)]
        self.img = OnscreenImage(
                'assets/images/cars/%s_sel.png' % self.mdt.car,
                parent=base.a2dBottomRight, pos=(-.5, 1, .5), scale=.4)
        self.widgets += [self.img]
        PageGui.build_page(self)

    def on_click(self, i):
        ts = TextureStage('ts')
        ts.setMode(TextureStage.MDecal)
        self.img.setTexture(ts, loader.loadTexture('assets/images/drivers/driver%s_sel.png' % i))
        taskMgr.doMethodLater(2.0, lambda tsk: game.fsm.demand('Race', self.mdt.track, self.mdt.car, [], str(i)), 'start')

    def destroy(self):
        PageGui.destroy(self)
        self.img = None


class DriverPage(Page):
    gui_cls = DriverPageGui

    def __init__(self, menu, track, car):
        self.track = track
        self.car = car
        Page.__init__(self, menu)
