from abc import ABCMeta
from racing.game.gameobject import GameObjectMdt
from .logic import _Logic


class Season(GameObjectMdt):
    __metaclass__ = ABCMeta
    logic_cls = _Logic

    @property
    def init_lst(self):
        return [
            [(self.build_fsm, 'Fsm')],
            [(self.build_gfx, 'Gfx')],
            [(self.build_phys, 'Phys')],
            [(self.build_gui, 'Gui')],
            [(self.build_logic, '_Logic')],
            [(self.build_audio, 'Audio')],
            [(self.build_ai, 'Ai')],
            [(self.build_event, 'Event')]]
