from racing.game.gameobject import Logic


class _Logic(Logic):

    def __init__(self, mdt):
        Logic.__init__(self, mdt)

    @staticmethod
    def start():
        game.fsm.demand('Loading')
