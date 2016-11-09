from racing.game.gameobject import Gui
from .tutorial import Tutorial
from .results import Results


class RaceGui(Gui):

    def __init__(self, mdt):
        Gui.__init__(self, mdt)
        self.tutorial = Tutorial()
        self.results = Results()

    def destroy(self):
        Gui.destroy(self)
        self.tutorial.destroy()
        self.results.destroy()
