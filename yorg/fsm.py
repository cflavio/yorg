from racing.car.car import Car, PlayerCar, NetworkCar, AiCar
from racing.track.track import Track
from racing.race.race import Race
from racing.game.gameobject.gameobject import Fsm
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import NodePath, TextNode
from menu.menu import YorgMenu


class NetMsgs(object):

    client_ready = 0
    start_race = 1


class _Fsm(Fsm):

    def __init__(self, mdt):
        Fsm.__init__(self, mdt)
        self.defaultTransitions = {
            'Menu': ['Loading'],
            'Loading': ['Play'],
            'Play': ['Ranking', 'Menu'],
            'Ranking': ['Play', 'Menu']}
        self.load_txt = None
        self.preview = None
        self.cam_tsk = None
        self.cam_node = None
        self.ranking_texts = None
        self.send_tsk = None
        self.cam_pivot = None
        self.ready_clients = None
        self.curr_load_txt = None
        self.__menu = None

    def enterMenu(self):
        eng.log_mgr.log('entering Menu state')
        self.__menu = YorgMenu()
        self.mdt.audio.menu_music.play()

    def exitMenu(self):
        eng.log_mgr.log('exiting Menu state')
        self.__menu.destroy()
        self.mdt.audio.menu_music.stop()

    def enterLoading(self, track_path='', car_path='', player_cars=[]):
        # class loading
        eng.log_mgr.log('entering Loading state')
        eng.gfx.init()
        if not track_path and not car_path:
            tracks = ['prototype', 'desert']
            track = tracks[tracks.index(game.options['last_track']) + 1]
            track_path = 'tracks/' + track
            car_path = game.options['last_car']
        conf = game.options
        conf['last_track'] = track_path[7:]
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
            self.preview = loader.loadModel(track_path+'/preview/preview.bam')
        self.preview.reparent_to(render)
        self.cam_pivot = NodePath('cam pivot')
        self.cam_pivot.reparent_to(render)
        self.cam_node = NodePath('cam node')
        self.cam_node.set_pos(500, 0, 0)
        self.cam_node.reparent_to(self.cam_pivot)
        hpr = (360, 0, 0)
        self.cam_pivot.hprInterval(25, hpr, blendType='easeInOut').loop()
        self.cam_tsk = taskMgr.add(self.update_cam, 'update cam')
        args = [track_path, car_path, player_cars]
        taskMgr.doMethodLater(1.0, self.load_stuff, 'loading stuff', args)

    def on_loading(self, msg):
        self.curr_load_txt.setText(msg)

    def update_cam(self, task):
        # class loading
        pos = self.cam_node.get_pos(render)
        eng.base.camera.set_pos(pos[0], pos[1], 1000)
        eng.base.camera.look_at(0, 0, 0)
        return task.again

    def load_stuff(self, track_path, car_path, player_cars):
        # class loading
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
                    return
                car = cars[0]
                cars.remove(car)
                car_class = Car
                ai = True
                if eng.server.is_active:
                    car_class = NetworkCar if car in player_cars else Car
                if eng.client.is_active:
                    car_class = NetworkCar
                pos = self.mdt.track.gfx.get_start_pos(grid.index(car))[0]
                hpr = self.mdt.track.gfx.get_start_pos(grid.index(car))[1]
                func = load_other_cars
                no_p = car not in player_cars
                car_class = AiCar if no_p else car_class
                new_car = car_class('cars/' + car, pos, hpr, func, self.race,
                                    self.mdt.options['laps'])
                self.mdt.cars += [new_car]
            path = 'cars/' + car_path
            pos = self.mdt.track.gfx.get_start_pos(grid.index(car_path))[0]
            hpr = self.mdt.track.gfx.get_start_pos(grid.index(car_path))[1]
            func = load_other_cars
            car_cls = AiCar if ai else PlayerCar
            self.mdt.player_car = car_cls(path, pos, hpr, func, self.race,
                                          self.mdt.options['laps'])
            self.mdt.cars = []
        self.mdt.track = Track(
            track_path, load_car, game.options['split_world'],
            game.options['submodels'])
        self.mdt.track.gfx.attach(self.on_loading)
        self.race = Race()
        self.race.track = self.mdt.track

    def exitLoading(self):
        # class loading
        self.mdt.player_car.event.attach(self.race.event.on_wrong_way)
        self.mdt.player_car.event.attach(self.race.event.on_end_race)
        eng.log_mgr.log('exiting Loading state')
        self.preview.remove_node()
        self.cam_pivot.remove_node()
        self.load_txt.destroy()
        self.curr_load_txt.destroy()
        taskMgr.remove(self.cam_tsk)
        eng.base.camera.set_pos(0, 0, 0)

    def enterPlay(self, track_path, car_path):
        # class race
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
            # the server could not be listen to this event if it is still
            # loading we should do a global protocol, perhaps
        else:
            self.start_play()

    def process_srv(self, data_lst, sender):
        # class race
        if data_lst[0] == NetMsgs.client_ready:
            ipaddr = sender.getAddress().getIpString()
            eng.log_mgr.log('client ready: ' + ipaddr)
            self.ready_clients += [sender]
            connections = eng.server.connections
            if all(client in self.ready_clients for client in connections):
                self.start_play()
                eng.server.send([NetMsgs.start_race])

    def process_client(self, data_lst, sender):
        # class race
        if data_lst[0] == NetMsgs.start_race:
            eng.log_mgr.log('start race')
            taskMgr.remove(self.send_tsk)
            self.start_play()

    def start_play(self):
        # class race
        eng.phys.start()
        game.track.event.start()
        game.player_car.event.eval_register()
        self.mdt.audio.game_music.play()
        cars = [self.mdt.player_car] + self.mdt.cars
        map(lambda car: car.event.reset_car(), cars)
        map(lambda car: car.event.start(), cars)

    def exitPlay(self):
        # class race
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

    def __step(self):
        # class tournament
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

    def enterRanking(self):
        # class tournament
        items = game.ranking.items()
        sorted_ranking = reversed(sorted(items, key=lambda el: el[1]))
        font = eng.font_mgr.load_font('assets/fonts/zekton rg.ttf')
        self.ranking_texts = []
        for i, (name, score) in enumerate(sorted_ranking):
            txt = OnscreenText(
                '%s %s' % (name, score), pos=(0, .5 -.2 * i), font=font,
                fg=(.75, .75, .75, 1), scale=.12)
            self.ranking_texts += [txt]
        taskMgr.doMethodLater(10, lambda task: self.__step(), 'step')

    def exitRanking(self):
        map(lambda txt: txt.destroy(), self.ranking_texts)
