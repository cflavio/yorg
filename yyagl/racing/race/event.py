from itertools import chain
from direct.interval.LerpInterval import LerpPosInterval, LerpHprInterval
from yyagl.gameobject import Event
from yyagl.racing.car.ai import CarAi


class NetMsgs(object):
    game_packet = 0
    player_info = 1
    end_race_player = 2
    end_race = 3


class RaceEvent(Event):

    def __init__(self, mdt):
        Event.__init__(self, mdt)
        self.accept('p', eng.pause.logic.toggle)
        self.last_sent = globalClock.getFrameTime()

    def network_register(self):
        pass

    def on_wrong_way(self, way_str):
        self.mdt.track.gui.way_txt.setText(way_str)

    def on_end_race(self):
        points = [10,8, 6]
        race_ranking = {car: point for car, point in zip(self.mdt.logic.ranking(), points)}
        self.mdt.fsm.demand('Results', race_ranking)


class RaceEventServer(RaceEvent):

    def __init__(self, mdt):
        RaceEvent.__init__(self, mdt)
        self.server_info = {}
        eng.event.attach(self.on_frame)

    def network_register(self):
        eng.server.register_cb(self.process_srv)

    def on_frame(self):
        if not hasattr(game, 'player_car') or \
                not hasattr(game.player_car, 'phys') or \
                any([not hasattr(car, 'phys') for car in game.cars]):
            return  # still loading; attach when the race has started
        pos = game.player_car.gfx.nodepath.getPos()
        hpr = game.player_car.gfx.nodepath.getHpr()
        velocity = game.player_car.phys.vehicle.getChassis().getLinearVelocity()
        self.server_info['server'] = (pos, hpr, velocity)
        for car in [car for car in game.cars if car.ai_cls == _Ai]:
            pos = car.gfx.nodepath.getPos()
            hpr = car.gfx.nodepath.getHpr()
            velocity = car.phys.vehicle.getChassis().getLinearVelocity()
            self.server_info[car] = (pos, hpr, velocity)
        if globalClock.getFrameTime() - self.last_sent > .2:
            eng.server.send(self.__prepare_game_packet())
            self.last_sent = globalClock.getFrameTime()

    @staticmethod
    def __prepare_game_packet():
        packet = [NetMsgs.game_packet]
        for car in [game.player_car] + game.cars:
            name = car.gfx.path
            pos = car.gfx.nodepath.getPos()
            hpr = car.gfx.nodepath.getHpr()
            velocity = car.phys.vehicle.getChassis().getLinearVelocity()
            packet += chain([name], pos, hpr, velocity)
        return packet

    def __process_player_info(self, data_lst, sender):
        from racing.car.car import NetworkCar
        pos = (data_lst[1], data_lst[2], data_lst[3])
        hpr = (data_lst[4], data_lst[5], data_lst[6])
        velocity = (data_lst[7], data_lst[8], data_lst[9])
        self.server_info[sender] = (pos, hpr, velocity)
        car_name = eng.server.car_mapping[sender]
        for car in [car for car in game.cars if car.__class__ == NetworkCar]:
            if car_name in car.gfx.path:
                LerpPosInterval(car.gfx.nodepath, .2, pos).start()
                LerpHprInterval(car.gfx.nodepath, .2, hpr).start()

    def process_srv(self, data_lst, sender):
        if data_lst[0] == NetMsgs.player_info:
            self.__process_player_info(data_lst, sender)
        if data_lst[0] == NetMsgs.end_race_player:
            eng.server.send([NetMsgs.end_race])
            dct = {'kronos': 0, 'themis': 0, 'diones': 0}
            game.fsm.race.fsm.demand('Results', dct)
            # forward the actual ranking
            game.fsm.race.gui.results.show(dct)

    def destroy(self):
        eng.event.detach(self.on_frame)
        RaceEvent.destroy(self)


class RaceEventClient(RaceEvent):

    def network_register(self):
        eng.client.register_cb(self.process_client)

    @staticmethod
    def __process_game_packet(data_lst):
        from racing.car.car import NetworkCar
        for i in range(1, len(data_lst), 10):
            car_name = data_lst[i]
            car_pos = (data_lst[i + 1], data_lst[i + 2], data_lst[i + 3])
            car_hpr = (data_lst[i + 4], data_lst[i + 5], data_lst[i + 6])
            netcars = [car for car in game.cars if car.__class__ == NetworkCar]
            for car in netcars:
                if car_name in car.gfx.path:
                    LerpPosInterval(car.gfx.nodepath, .2, car_pos).start()
                    LerpHprInterval(car.gfx.nodepath, .2, car_hpr).start()

    def process_client(self, data_lst, sender):
        if data_lst[0] == NetMsgs.game_packet:
            self.__process_game_packet(data_lst)
        if data_lst[0] == NetMsgs.end_race:
            if game.fsm.race.fsm.getCurrentOrNextState() != 'Results':
                # forward the actual ranking
                dct = {'kronos': 0, 'themis': 0, 'diones': 0}
                game.fsm.race.fsm.demand('Results', dct)
