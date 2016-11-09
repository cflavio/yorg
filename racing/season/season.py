from abc import ABCMeta
from racing.game.gameobject import GameObjectMdt
from .logic import SeasonLogic, SingleRaceSeasonLogic


class Season(GameObjectMdt):
    __metaclass__ = ABCMeta
    logic_cls = SeasonLogic

    def __init__(self, init_lst=[]):
        init_lst = [
            [('fsm', self.fsm_cls, [self])],
            [('gfx', self.gfx_cls, [self])],
            [('phys', self.phys_cls, [self])],
            [('gui', self.gui_cls, [self])],
            [('logic', self.logic_cls, [self])],
            [('audio', self.audio_cls, [self])],
            [('ai', self.ai_cls, [self])],
            [('event', self.event_cls, [self])]]
        GameObjectMdt.__init__(self, init_lst)


class SingleRaceSeason(Season):
    logic_cls = SingleRaceSeasonLogic
