'''In this module we define the global game classes.'''
from car.car import Car
from menu import Menu
from track.track import Track
from ya2.game import Game, GameLogic
from ya2.gameobject import Event, Fsm, Audio
import time


class _Event(Event):
    '''This class manages the events of the game.'''

    def __init__(self, mdt):
        Event.__init__(self, mdt)
        self.accept('f12', eng.toggle_debug)
        now = time.strftime('%y_%m_%d_%H_%M_%S')
        self.accept('f10', eng.win.saveScreenshot, ['yorg_' + now + '.png'])

class _Audio(Audio):

    def __init__(self, mdt):
        Audio.__init__(self, mdt)
        self.menu_music = loader.loadSfx('assets/music/menu.ogg')
        self.game_music = loader.loadSfx('assets/music/on_the_other_side.ogg')
        map(lambda mus: mus.set_loop(True), [self.menu_music, self.game_music])


class _Fsm(Fsm):
    '''This class defines the game FMS.'''

    def __init__(self, mdt):
        Fsm.__init__(self, mdt)
        self.defaultTransitions = {'Menu': ['Play'],
                                   'Play': ['Menu']}

    def enterMenu(self):
        self.__menu = Menu(self)
        self.mdt.audio.menu_music.play()

    def exitMenu(self):
        self.__menu.destroy()
        self.mdt.audio.menu_music.stop()

    def enterPlay(self):
        eng.start()
        self.mdt.track = Track()
        self.mdt.car = Car(self.mdt.track.gfx.start_pos,
                         self.mdt.track.gfx.start_pos_hpr)
        self.mdt.audio.game_music.play()

    def exitPlay(self):
        self.mdt.audio.game_music.stop()
        self.mdt.track.destroy()
        self.mdt.car.destroy()


class _Logic(GameLogic):
    '''This class defines the logics of the game.'''

    def run(self):
        GameLogic.run(self)
        self.mdt.fsm.demand('Menu')


class Yorg(Game):
    logic_cls = _Logic
    event_cls = _Event
    fsm_cls = _Fsm
    audio_cls = _Audio
