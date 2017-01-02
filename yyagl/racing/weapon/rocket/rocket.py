from yyagl.gameobject import GameObjectMdt
from .gfx import RocketGfx
from .phys import RocketPhys
from .audio import RocketAudio
from .logic import RocketLogic


class Rocket(GameObjectMdt):
    gfx_cls = RocketGfx
    phys_cls = RocketPhys
    audio_cls = RocketAudio
    logic_cls = RocketLogic

    def __init__(self, car):
        self.car = car
        init_lst = [
            [('gfx', self.gfx_cls, [self])],
            [('phys', self.phys_cls, [self])],
            [('audio', self.audio_cls, [self])],
            [('logic', self.logic_cls, [self])]]
        GameObjectMdt.__init__(self, init_lst)

    def destroy(self):
        GameObjectMdt.destroy(self)
        self.car = None
