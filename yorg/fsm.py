from racing.car.car import Car, PlayerCar, NetworkCar
from racing.track.track import Track
from racing.game.game import Game, GameLogic
from racing.game.gameobject.gameobject import Event, Fsm, Audio
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from racing.track.gfx import _Gfx as TrackGfx
from racing.car.gfx import _Gfx as CarGfx
from panda3d.core import NodePath, TextNode
from direct.interval.LerpInterval import LerpHprInterval
from racing.game.engine.gui.mainpage import MainPage, MainPageGui
from racing.game.engine.gui.page import Page, PageEvent, PageGui
from racing.game.gameobject.gameobject import Fsm
from menu.menu import YorgMenu


class NetMsgs:

    client_ready = 0
    start_race = 1


class _Fsm(Fsm):
    '''This class defines the game FMS.'''

    def __init__(self, mdt):
        Fsm.__init__(self, mdt)
        self.defaultTransitions = {'Menu': ['Loading'],
                                   'Loading': ['Play'],
                                   'Play': ['Ranking', 'Menu'],
                                   'Ranking': ['Play', 'Menu']}

    def enterMenu(self):
        eng.log_mgr.log('entering Menu state')
        self.__menu = YorgMenu()
        self.mdt.audio.menu_music.play()

    def exitMenu(self):
        eng.log_mgr.log('exiting Menu state')
        self.__menu.destroy()
        self.mdt.audio.menu_music.stop()

    def enterLoading(self, track_path='', car_path='', player_cars=[]):
        eng.log_mgr.log('entering Loading state')
        eng.gfx.init()
        if not track_path and not car_path:
            tracks = ['prototype', 'desert']
            track = tracks[tracks.index(game.options['last_track']) + 1]
            track_path = 'tracks/track_' + track
            car_path = game.options['last_car']
        conf = game.options
        conf['last_track'] = track_path[13:]
        conf['last_car'] = car_path
        conf.store()
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
        taskMgr.doMethodLater(1.0, self.load_stuff, 'loading stuff', [track_path, car_path, player_cars])

    def update_cam(self, task):
        pos = self.cam_node.get_pos(render)
        eng.base.camera.set_pos(pos[0], pos[1], 1000)
        eng.base.camera.look_at(0, 0, 0)
        return task.again

    def load_stuff(self, track_path, car_path, player_cars):
        eng.phys.init()
        player_cars = player_cars[1::2]
        def load_car():
            cars = ['kronos', 'themis', 'diones']
            grid = ['kronos', 'themis', 'diones']
            cars.remove(car_path)
            ai = game.options['ai']
            def load_other_cars():
               if not cars:
                   self.mdt.fsm.demand('Play', track_path, car_path)
               else:
                   car = cars[0]
                   cars.remove(car)
                   car_class = Car
                   ai = True
                   if eng.server.is_active:
                       car_class = NetworkCar if car in player_cars else Car
                   if eng.client.is_active:
                       car_class = NetworkCar
                   self.mdt.cars += [
                       car_class('cars/' + car,
                            self.mdt.track.gfx.get_start_pos(grid.index(car))[0],
                            self.mdt.track.gfx.get_start_pos(grid.index(car))[1],
                            load_other_cars, car not in player_cars)]
            self.mdt.player_car = PlayerCar(
                'cars/' + car_path,
                self.mdt.track.gfx.get_start_pos(grid.index(car_path))[0],
                self.mdt.track.gfx.get_start_pos(grid.index(car_path))[1],
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
        eng.base.camera.set_pos(0, 0, 0)

    def enterPlay(self, track_path, car_path):
        eng.log_mgr.log('entering Play state')
        self.mdt.track.gfx.model.reparentTo(render)
        self.mdt.player_car.gfx.reparent()
        map(lambda car: car.gfx.reparent(), self.mdt.cars)
        if eng.server.is_active:
            self.ready_clients = []
            eng.server.register_cb(self.process_srv)
        elif eng.client.is_active:
            eng.client.register_cb(self.process_client)
            def send_ready(task):
                eng.client.send([NetMsgs.client_ready])
                eng.log_mgr.log('sent client ready')
                return task.again
            self.send_tsk = taskMgr.doMethodLater(.5, send_ready, 'send ready')
            # the server could not be listen to this event if it is still loading
            # we should do a global protocol, perhaps
        else:
            self.start_play()

    def process_srv(self, data_lst, sender):
        if data_lst[0] == NetMsgs.client_ready:
            eng.log_mgr.log('client ready: ' + sender.getAddress().getIpString())
            self.ready_clients += [sender]
            if all(client in self.ready_clients for client in eng.server.connections):
                self.start_play()
                eng.server.send([NetMsgs.start_race])

    def process_client(self, data_lst, sender):
        if data_lst[0] == NetMsgs.start_race:
            eng.log_mgr.log('start race')
            taskMgr.remove(self.send_tsk)
            self.start_play()

    def start_play(self):
        eng.phys.start()
        game.track.event.start()
        game.player_car.event.eval_register()
        self.mdt.audio.game_music.play()
        map(lambda car: car.event.reset_car(), [self.mdt.player_car] + self.mdt.cars)
        map(lambda car: car.event.start(), [self.mdt.player_car] + self.mdt.cars)

    def exitPlay(self):
        eng.log_mgr.log('exiting Play state')
        if eng.server.is_active:
            eng.server.destroy()
            eng.server = None
        elif eng.client.is_active:
            eng.client.destroy()
            eng.client = None
        self.mdt.audio.game_music.stop()
        self.mdt.track.destroy()
        self.mdt.player_car.destroy()
        map(lambda car: car.destroy(), self.mdt.cars)
        eng.phys.stop()
        eng.gfx.clean()

    def enterRanking(self):
        sorted_ranking = reversed(sorted(game.ranking.items(), key=lambda el: el[1]))
        font = eng.font_mgr.load_font('assets/fonts/zekton rg.ttf')
        self.ranking_texts = []
        for i, (name, score) in enumerate(sorted_ranking):
            self.ranking_texts += [OnscreenText(
                '%s %s' % (name, score), pos=(0, .5 -.2 * i), font=font,
                fg=(.75, .75, .75, 1), scale=.12)]
        def step(task):
            current_track = game.track.gfx.track_path[13:]
            tracks = ['prototype', 'desert']
            if tracks.index(current_track) == len(tracks) - 1:
                game.ranking = None
                conf = game.options
                del conf['last_car']
                del conf['last_track']
                del conf['last_ranking']
                conf.store()
                self.demand('Menu')
            else:
                next_track = tracks[tracks.index(current_track) + 1]
                curr_car = game.options['last_car']
                self.demand('Loading', next_track, curr_car)
        taskMgr.doMethodLater(10, step, 'step')

    def exitRanking(self):
        map(lambda txt: txt.destroy(), self.ranking_texts)
