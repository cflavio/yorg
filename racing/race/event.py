from racing.game.gameobject.gameobject import Event


class _Event(Event):

    def on_wrong_way(self, way_str):
        self.mdt.track.gui.way_txt.setText(way_str)
