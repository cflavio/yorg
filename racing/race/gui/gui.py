from racing.game.gameobject import Gui
from .countdown import Countdown
from .tutorial import Tutorial
from .results import Results


class RaceGui(Gui):

    def __init__(self, mdt):
        Gui.__init__(self, mdt)
        self.countdown = Countdown()
        self.countdown.attach(self.on_start_race)
        self.countdown = Tutorial()
        self.results = Results()

    def on_start_race(self):
        self.mdt.fsm.demand('Race')

    def destroy(self):
        Gui.destroy(self)
        self.countdown.destroy()
        self.tutorial.destroy()
        self.results.destroy()
