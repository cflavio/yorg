from racing.game.gameobject.gameobject import Fsm


class _Fsm(Fsm):

    def __init__(self, mdt):
        Fsm.__init__(self, mdt)
        self.defaultTransitions = {'Countdown': ['Race'],
                                   'Race': ['Results']}
