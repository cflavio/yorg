from direct.gui.OnscreenText import OnscreenText
from yyagl.gameobject import Gui
from yyagl.engine.gui.imgbtn import ImageButton
from direct.gui.OnscreenImage import OnscreenImage


class TuningGui(Gui):

    def show(self):
        self.background = OnscreenImage(
            'assets/images/gui/menu_background.jpg', scale=(1.77778, 1, 1.0))
        self.background.setBin('background', 10)
        self.buttons = [ImageButton(
            scale=.4, pos=(-1.2, 1, .1), frameColor=(0, 0, 0, 0),
            image='assets/images/tuning/engine.png',
            command=self.on_btn, extraArgs=['engine'])]
        self.buttons += [ImageButton(
            scale=.4, pos=(0, 1, .1), frameColor=(0, 0, 0, 0),
            image='assets/images/tuning/tires.png',
            command=self.on_btn, extraArgs=['tires'])]
        self.buttons += [ImageButton(
            scale=.4, pos=(1.2, 1, .1), frameColor=(0, 0, 0, 0),
            image='assets/images/tuning/suspensions.png',
            command=self.on_btn, extraArgs=['suspensions'])]

    def on_btn(self, val):
        self.mdt.logic.tuning[val] += 1
        game.logic.season.logic.step()

    def hide(self):
        map(lambda wdg: wdg.destroy(), self.buttons + [self.background])
