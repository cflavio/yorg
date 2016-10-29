from racing.game.gameobject import Event


class _Event(Event):

    def on_wrong_way(self, way_str):
        self.mdt.track.gui.way_txt.setText(way_str)

    @staticmethod
    def on_end_race():
        #TODO: compute the ranking
        race_ranking = {'kronos': 0, 'themis': 0, 'diones': 0}
        game.track.fsm.demand('Results', race_ranking)
