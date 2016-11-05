from panda3d.core import NodePath, TextNode
from direct.gui.OnscreenText import OnscreenText
from racing.game.gameobject import Logic
from racing.track.track import Track
from racing.car.car import Car, PlayerCar, PlayerCarServer, PlayerCarClient, \
    NetworkCar, AiCar


class NetMsgs(object):

    client_ready = 0
    start_race = 1


class RaceLogic(Logic):

    def __init__(self, mdt):
        self.load_txt = None
        self.cam_tsk = None
        self.cam_node = None
        self.send_tsk = None
        self.cam_pivot = None
        self.ready_clients = None
        self.preview = None
        self.curr_load_txt = None
        Logic.__init__(self, mdt)

    @staticmethod
    def start():
        game.fsm.demand('Loading')

    def enter_loading(self, track_path='', car_path='', player_cars=[]):
        eng.gfx.init()
        if not track_path and not car_path:
            tracks = ['prototype', 'desert']
            track = tracks[tracks.index(game.options['save']['track']) + 1]
            track_path = 'tracks/' + track
            car_path = game.options['save']['car']
        conf = game.options
        if 'save' not in conf.dct:
            conf['save'] = {}
        conf['save']['track'] = track_path[7:]
        conf['save']['car'] = car_path
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
        pos = self.cam_node.get_pos(render)
        eng.base.camera.set_pos(pos[0], pos[1], 1000)
        eng.base.camera.look_at(0, 0, 0)
        return task.again

    def load_stuff(self, track_path, car_path, player_cars):
        eng.phys.init()
        player_cars = player_cars[1::2]
        dev = game.options['development']

        def load_car():
            cars = ['kronos', 'themis', 'diones']
            grid = ['kronos', 'themis', 'diones']
            cars.remove(car_path)
            ai = dev['ai']

            def load_other_cars():
                if not cars:
                    game.fsm.demand('Play')
                    return
                car = cars[0]
                cars.remove(car)
                car_class = Car
                if eng.server.is_active:
                    car_class = NetworkCar  # if car in player_cars else Car
                if eng.client.is_active:
                    car_class = NetworkCar
                pos = game.track.gfx.get_start_pos(grid.index(car))[0]
                hpr = game.track.gfx.get_start_pos(grid.index(car))[1]
                func = load_other_cars
                no_p = car not in player_cars
                car_class = AiCar if no_p else car_class
                new_car = car_class('cars/' + car, pos, hpr, func, self.mdt,
                                    game.options['development']['laps'])
                game.cars += [new_car]
            path = 'cars/' + car_path
            pos = game.track.gfx.get_start_pos(grid.index(car_path))[0]
            hpr = game.track.gfx.get_start_pos(grid.index(car_path))[1]
            func = load_other_cars
            if ai:
                car_cls = AiCar
            else:
                car_cls = PlayerCar
                if eng.server.is_active:
                    car_cls = PlayerCarServer
                if eng.client.is_active:
                    car_cls = PlayerCarClient
            game.player_car = car_cls(path, pos, hpr, func, self.mdt,
                                      dev['laps'])
            game.cars = []
        game.track = Track(
            track_path, load_car, dev['split_world'], dev['submodels'])
        game.track.gfx.attach(self.on_loading)
        self.mdt.track = game.track

    def exit_loading(self):
        game.player_car.event.attach(self.mdt.event.on_wrong_way)
        game.player_car.event.attach(self.mdt.event.on_end_race)
        self.preview.remove_node()
        self.cam_pivot.remove_node()
        self.load_txt.destroy()
        self.curr_load_txt.destroy()
        taskMgr.remove(self.cam_tsk)
        eng.base.camera.set_pos(0, 0, 0)

    def enter_play(self):
        game.track.gfx.model.reparentTo(render)
        game.player_car.gfx.reparent()
        map(lambda car: car.gfx.reparent(), game.cars)
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
        if data_lst[0] == NetMsgs.client_ready:
            ipaddr = sender.getAddress().getIpString()
            eng.log_mgr.log('client ready: ' + ipaddr)
            self.ready_clients += [sender]
            connections = eng.server.connections
            if all(client in self.ready_clients for client in connections):
                self.start_play()
                eng.server.send([NetMsgs.start_race])

    def process_client(self, data_lst, sender):
        if data_lst[0] == NetMsgs.start_race:
            eng.log_mgr.log('start race')
            taskMgr.remove(self.send_tsk)
            self.start_play()

    @staticmethod
    def start_play():
        eng.phys.start()
        game.track.event.start()
        game.player_car.event.eval_register()
        game.audio.game_music.play()
        cars = [game.player_car] + game.cars
        map(lambda car: car.event.reset_car(), cars)
        map(lambda car: car.event.start(), cars)

    @staticmethod
    def exit_play():
        if eng.server.is_active:
            eng.server.destroy()
            eng.server = None
        elif eng.client.is_active:
            eng.client.destroy()
            eng.client = None
        game.audio.game_music.stop()
        game.track.destroy()
        game.player_car.destroy()
        map(lambda car: car.destroy(), game.cars)
        eng.phys.stop()
        eng.gfx.clean()
