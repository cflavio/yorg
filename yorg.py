'''In this module we define the global game classes.'''
from car.car import Car, PlayerCar
from menu import Menu
from track.track import Track
from ya2.game import Game, GameLogic
from ya2.gameobject import Event, Fsm, Audio
import time
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from track.gfx import _Gfx as TrackGfx
from car.gfx import _Gfx as CarGfx
from panda3d.core import NodePath, TextNode
from direct.interval.LerpInterval import LerpHprInterval
from ya2.engine import OptionMgr


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
        self.defaultTransitions = {'Menu': ['Loading'],
                                   'Loading': ['Play'],
                                   'Play': ['Menu']}

    def enterMenu(self):
        eng.log_mgr.log('entering Menu state')
        self.__menu = Menu(self)
        self.mdt.audio.menu_music.play()

    def exitMenu(self):
        eng.log_mgr.log('exiting Menu state')
        self.__menu.destroy()
        self.mdt.audio.menu_music.stop()

    def enterLoading(self, track_path, car_path):
        eng.log_mgr.log('entering Loading state')
        font = eng.font_mgr.load_font('assets/fonts/zekton rg.ttf')
        self.load_txt = OnscreenText(
            text=_('LOADING...\n\nPLEASE WAIT, IT MAY REQUIRE SOME TIME'),
            scale=.12, pos=(0, .4), font=font, fg=(.75, .75, .75, 1),
            wordwrap=12)
        self.curr_load_txt = OnscreenText(
            text='',
            scale=.08, pos=(-.1, .1), font=font, fg=(.75, .75, .75, 1),
            parent=base.a2dBottomRight, align=TextNode.A_right)
        try:
            self.preview = loader.loadModel(track_path + '/preview/preview')
        except IOError:
            self.preview = loader.loadModel(track_path + '/preview/preview.bam')
        self.preview.reparent_to(render)
        self.cam_pivot = NodePath('cam pivot')
        self.cam_pivot.reparent_to(render)
        self.cam_node = NodePath('cam node')
        self.cam_node.set_pos(500, 0, 0)
        self.cam_node.reparent_to(self.cam_pivot)
        self.cam_pivot.hprInterval(25, (360, 0, 0), blendType='easeInOut').loop()
        self.cam_tsk = taskMgr.add(self.update_cam, 'update cam')
        taskMgr.doMethodLater(1.0, self.load_stuff, 'loading stuff', [track_path, car_path])

    def update_cam(self, task):
        pos = self.cam_node.get_pos(render)
        eng.camera.set_pos(pos[0], pos[1], 1000)
        eng.camera.look_at(0, 0, 0)
        return task.again

    def load_stuff(self, track_path, car_path):
        eng.init()
        def load_car():
            cars = ['kronos', 'themis', 'diones']
            cars.remove(car_path)
            ai = OptionMgr.get_options()['ai']
            def load_other_cars():
               if not cars:
                   self.mdt.fsm.demand('Play', track_path, car_path)
               else:
                   car = cars[0]
                   cars.remove(car)
                   self.mdt.cars += [
                       Car('cars/' + car,
                            self.mdt.track.gfx.get_start_pos(len(cars))[0],
                            self.mdt.track.gfx.get_start_pos(len(cars))[1],
                            load_other_cars, True)]
            self.mdt.player_car = PlayerCar(
                'cars/' + car_path,
                self.mdt.track.gfx.get_start_pos(len(cars))[0],
                self.mdt.track.gfx.get_start_pos(len(cars))[1],
                load_other_cars, ai)
            self.mdt.cars = []
        self.mdt.track = Track(track_path, load_car)

    def exitLoading(self):
        eng.log_mgr.log('exiting Loading state')
        self.preview.remove_node()
        self.cam_pivot.remove_node()
        self.load_txt.destroy()
        self.curr_load_txt.destroy()
        taskMgr.remove(self.cam_tsk)
        eng.camera.set_pos(0, 0, 0)

    def enterPlay(self, track_path, car_path):
        eng.log_mgr.log('entering Play state')
        self.mdt.track.gfx.model.reparentTo(render)
        self.mdt.player_car.gfx.reparent()
        map(lambda car: car.gfx.reparent(), self.mdt.cars)
        eng.start()
        self.mdt.audio.game_music.play()

    def exitPlay(self):
        eng.log_mgr.log('exiting Play state')
        self.mdt.audio.game_music.stop()
        self.mdt.track.destroy()
        self.mdt.player_car.destroy()
        map(lambda car: car.destroy(), self.mdt.cars)


class _Logic(GameLogic):
    '''This class defines the logics of the game.'''

    def run(self):
        GameLogic.run(self)
        try:
            car = OptionMgr.get_options()['car']
        except KeyError:
            car = ''
        try:
            track = OptionMgr.get_options()['track']
        except KeyError:
            track = ''
        if car and track:
            self.mdt.fsm.demand('Loading', 'tracks/track_' + track, car)
        else:
            self.mdt.fsm.demand('Menu')


class Yorg(Game):
    logic_cls = _Logic
    event_cls = _Event
    fsm_cls = _Fsm
    audio_cls = _Audio
