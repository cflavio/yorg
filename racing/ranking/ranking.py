from abc import ABCMeta
from racing.game.gameobject import GameObjectMdt
from .logic import RankingLogic
from .gui import RankingGui


class Ranking(GameObjectMdt):
    __metaclass__ = ABCMeta
    logic_cls = RankingLogic
    gui_cls = RankingGui

    def __init__(self, init_lst=[]):
        init_lst = [
            [(self.build_fsm, 'Fsm')],
            [(self.build_gfx, 'Gfx')],
            [(self.build_phys, 'Phys')],
            [(self.build_gui, 'RankingGui')],
            [(self.build_logic, 'RankingLogic')],
            [(self.build_audio, 'Audio')],
            [(self.build_ai, 'Ai')],
            [(self.build_event, 'Event')]]
        GameObjectMdt.__init__(self, init_lst)
