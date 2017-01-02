from panda3d.core import NodePath, TextNode
from direct.gui.OnscreenText import OnscreenText
from yyagl.gameobject import Logic
from yyagl.racing.track.track import Track
from yyagl.racing.car.car import Car, PlayerCar, PlayerCarServer, \
    PlayerCarClient, NetworkCar, AiCar


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
        game.fsm.demand('Race')

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
                    game.fsm.race.fsm.demand('Countdown')
                    return
                car = cars[0]
                cars.remove(car)
                car_class = Car
                if eng.server.is_active:
                    car_class = NetworkCar  # if car in player_cars else Car
                if eng.client.is_active:
                    car_class = NetworkCar
                pos = game.track.phys.get_start_pos(grid.index(car))[0]
                hpr = game.track.phys.get_start_pos(grid.index(car))[1]
                func = load_other_cars
                no_p = car not in player_cars
                srv_or_sng = eng.server.is_active or not eng.client.is_active
                car_class = AiCar if no_p and srv_or_sng else car_class
                new_car = car_class('cars/' + car, pos, hpr, func, self.mdt,
                                    game.options['development']['laps'])
                game.cars += [new_car]
            path = 'cars/' + car_path
            pos = game.track.phys.get_start_pos(grid.index(car_path))[0]
            hpr = game.track.phys.get_start_pos(grid.index(car_path))[1]
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
        game.track.attach(self.mdt.gui.loading.on_loading)
        self.mdt.track = game.track

    def enter_play(self):
        game.track.gfx.model.reparentTo(eng.gfx.world_np)
        game.player_car.gfx.reparent()
        map(lambda car: car.gfx.reparent(), game.cars)

    def start_play(self):
        eng.phys.start()
        game.track.event.start()
        self.mdt.event.network_register()
        game.audio.game_music.play()
        cars = [game.player_car] + game.cars
        map(lambda car: car.logic.reset_car(), cars)
        map(lambda car: car.event.start(), cars)

    def ranking(self):
        cars = [game.player_car] + game.cars
        info = []
        for car in cars:
            past_wp = car.logic.closest_wp()[0].get_pos()
            wp_num = int(car.logic.closest_wp()[0].get_name()[8:])
            dist = (past_wp - car.gfx.nodepath.get_pos()).length()
            info += [(car.path[5:], len(car.logic.lap_times), wp_num, dist)]
        by_dist = sorted(info, key=lambda val: val[3])
        by_wp_num = sorted(by_dist, key=lambda val: val[2])
        by_laps = sorted(by_wp_num, key=lambda val: val[1])
        return [car[0] for car in reversed(by_laps)]

    @staticmethod
    def exit_play():
        game.audio.game_music.stop()
        game.track.destroy()
        game.player_car.destroy()
        map(lambda car: car.destroy(), game.cars)
        eng.phys.stop()
        eng.gfx.clean()


class RaceLogicSinglePlayer(RaceLogic):

    def enter_play(self):
        RaceLogic.enter_play(self)
        self.start_play()


class RaceLogicServer(RaceLogic):

    def enter_play(self):
        RaceLogic.enter_play(self)
        self.ready_clients = []
        eng.server.register_cb(self.process_srv)

    def process_srv(self, data_lst, sender):
        if data_lst[0] == NetMsgs.client_ready:
            ipaddr = sender.getAddress().getIpString()
            eng.log_mgr.log('client ready: ' + ipaddr)
            self.ready_clients += [sender]
            connections = eng.server.connections
            if all(client in self.ready_clients for client in connections):
                self.start_play()
                eng.server.send([NetMsgs.start_race])

    @staticmethod
    def exit_play():
        eng.server.destroy()
        eng.server = None
        RaceLogic.exit_play()


class RaceLogicClient(RaceLogic):

    def enter_play(self):
        RaceLogic.enter_play(self)
        eng.client.register_cb(self.process_client)

        def send_ready(task):
            eng.client.send([NetMsgs.client_ready])
            eng.log_mgr.log('sent client ready')
            return task.again
        self.send_tsk = taskMgr.doMethodLater(.5, send_ready, 'send ready')
        # the server could not be listen to this event if it is still
        # loading we should do a global protocol, perhaps

    def process_client(self, data_lst, sender):
        if data_lst[0] == NetMsgs.start_race:
            eng.log_mgr.log('start race')
            taskMgr.remove(self.send_tsk)
            self.start_play()

    @staticmethod
    def exit_play():
        eng.client.destroy()
        eng.client = None
        RaceLogic.exit_play()
