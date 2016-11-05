from racing.game.gameobject import Event


class _Event(Event):

    def on_wrong_way(self, way_str):
        self.mdt.track.gui.way_txt.setText(way_str)

    def on_end_race(self):
        #TODO: compute the ranking
        race_ranking = {'kronos': 0, 'themis': 0, 'diones': 0}
        self.mdt.fsm.demand('Results', race_ranking)
