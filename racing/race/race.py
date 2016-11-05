from abc import ABCMeta
from racing.game.gameobject import GameObjectMdt
from .logic import _Logic
from .event import _Event
from .gui.gui import _Gui
from .fsm import _Fsm


class Race(GameObjectMdt):
    __metaclass__ = ABCMeta
    logic_cls = _Logic
    event_cls = _Event
    gui_cls = _Gui
    fsm_cls = _Fsm

    @property
    def init_lst(self):
        return [
            [(self.build_fsm, '_Fsm')],
            [(self.build_gfx, 'Gfx')],
            [(self.build_phys, 'Phys')],
            [(self.build_gui, '_Gui')],
            [(self.build_logic, '_Logic')],
            [(self.build_audio, 'Audio')],
            [(self.build_ai, 'Ai')],
            [(self.build_event, '_Event')]]
