from racing.game.gameobject import Fsm


class _Fsm(Fsm):

    def __init__(self, mdt):
        Fsm.__init__(self, mdt)
        self.defaultTransitions = {'Countdown': ['Race'],
                                   'Race': ['Results']}

    def enterResults(self, race_ranking):
        self.mdt.gui.results.show(race_ranking)
