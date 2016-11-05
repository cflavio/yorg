from abc import ABCMeta
from racing.game.gameobject import GameObjectMdt
from .logic import SeasonLogic


class Season(GameObjectMdt):
    __metaclass__ = ABCMeta
    logic_cls = SeasonLogic

    def __init__(self, init_lst=[]):
        init_lst = [
            [(self.build_fsm, 'Fsm')],
            [(self.build_gfx, 'Gfx')],
            [(self.build_phys, 'Phys')],
            [(self.build_gui, 'Gui')],
            [(self.build_logic, 'SeasonLogic')],
            [(self.build_audio, 'Audio')],
            [(self.build_ai, 'Ai')],
            [(self.build_event, 'Event')]]
        GameObjectMdt.__init__(self, init_lst)

