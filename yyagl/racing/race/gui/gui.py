from yyagl.gameobject import Gui
from .tutorial import Tutorial
from .results import Results
from .loading import Loading


class RaceGui(Gui):

    def __init__(self, mdt):
        Gui.__init__(self, mdt)
        self.tutorial = Tutorial()
        self.results = Results()
        self.loading = Loading(mdt)

    def destroy(self):
        Gui.destroy(self)
        self.tutorial.destroy()
        self.results.destroy()
        self.loading.destroy()
