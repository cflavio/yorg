from yyagl.gameobject import GameObjectMdt
from .gfx import BonusGfx
from .phys import BonusPhys
from .event import BonusEvent


class Bonus(GameObjectMdt):
    gfx_cls = BonusGfx
    phys_cls = BonusPhys
    event_cls = BonusEvent

    def __init__(self, pos):
        init_lst = [[('gfx', self.gfx_cls, [self, pos])],
                    [('event', self.event_cls, [self])],
                    [('phys', self.phys_cls, [self, pos])]]
        GameObjectMdt.__init__(self, init_lst)
