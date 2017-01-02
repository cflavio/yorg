from yyagl.gameobject import GameObjectMdt
from .logic import SeasonLogic, SingleRaceSeasonLogic


class Season(GameObjectMdt):
    logic_cls = SeasonLogic

    def __init__(self):
        init_lst = [[('logic', self.logic_cls, [self])]]
        GameObjectMdt.__init__(self, init_lst)


class SingleRaceSeason(Season):
    logic_cls = SingleRaceSeasonLogic
