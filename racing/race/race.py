from abc import ABCMeta
from racing.game.gameobject import GameObjectMdt
from .logic import RaceLogic
from .event import _Event
from .gui.gui import RaceGui
from .fsm import _Fsm


class Race(GameObjectMdt):
    __metaclass__ = ABCMeta
    logic_cls = RaceLogic
    event_cls = _Event
    gui_cls = RaceGui
    fsm_cls = _Fsm

    def __init__(self, init_lst=[]):
        init_lst = [
            [(self.build_fsm, '_Fsm')],
            [(self.build_gfx, 'Gfx')],
            [(self.build_phys, 'Phys')],
            [(self.build_gui, 'RaceGui')],
            [(self.build_logic, 'RaceLogic')],
            [(self.build_audio, 'Audio')],
            [(self.build_ai, 'Ai')],
            [(self.build_event, '_Event')]]
        GameObjectMdt.__init__(self, init_lst)
