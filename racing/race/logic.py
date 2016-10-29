from racing.game.gameobject.gameobject import Logic


class _Logic(Logic):

    def __init__(self, mdt):
        Logic.__init__(self, mdt)

    def start(self):
        game.fsm.demand('Loading')
