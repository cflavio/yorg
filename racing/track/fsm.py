from racing.game.gameobject.gameobject import Fsm


class _Fsm(Fsm):
    '''This class defines the game FMS.'''

    def __init__(self, mdt):
        Fsm.__init__(self, mdt)
        self.defaultTransitions = {'Countdown': ['Race'],
                                   'Race': ['Results']}
