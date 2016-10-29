from itertools import chain
from direct.showbase.InputStateGlobal import inputState
from racing.game.gameobject.gameobject import Event
from panda3d.core import AudioSound, Vec3, Vec2
from .ai import _Ai
from direct.interval.LerpInterval import LerpPosInterval, LerpHprInterval


class _Event(Event):

    def __init__(self, mdt):
        self.tsk = None
        Event.__init__(self, mdt)
        eng.phys.attach(self.on_collision)
        label_events = [
            ('forward', 'arrow_up'), ('left', 'arrow_left'), ('reverse', 'z'),
            ('reverse', 'arrow_down'), ('right', 'arrow_right')]
        watch = inputState.watchWithModifiers
        map(lambda (lab, evt): watch(lab, evt), label_events)

    def start(self):
        eng.event.attach(self.on_frame)

    def __process_respawn(self):
        last_pos = self.mdt.logic.last_contact_pos
        start_wp_n, end_wp_n = self.mdt.logic.closest_wp(last_pos)
        #start_wp, end_wp = start_wp_n.get_pos(), end_wp_n.get_pos()
        # A + dot(AP,AB) / dot(AB,AB) * AB
        #point_vec = Vec3(last_pos.x - start_wp.x,
        #                 last_pos.y - start_wp.y,
        #                 last_pos.z - start_wp.z)
        #wp_vec = Vec3(end_wp.x - start_wp.x,
        #              end_wp.y - start_wp.y,
        #              end_wp.z - start_wp.z)
        #dot_point = point_vec.dot(wp_vec)
        #dot_wp = wp_vec.dot(wp_vec)
        #delta = wp_vec * (dot_point / dot_wp)
        #new_pos = start_wp + delta
        new_pos = start_wp_n.get_pos()
        self.mdt.gfx.nodepath.setPos(new_pos.x, new_pos.y, new_pos.z + 2)

        wp_vec = Vec3(end_wp_n.getPos(start_wp_n).xy, 0)
        wp_vec.normalize()
        or_h = (wp_vec.xy).signedAngleDeg(Vec2(0, 1))
        self.mdt.gfx.nodepath.setHpr(-or_h, 0, 0)
        self.mdt.gfx.nodepath.node().setLinearVelocity(0)
        self.mdt.gfx.nodepath.node().setAngularVelocity(0)

    def on_collision(self, obj, obj_name):
        if obj != self.mdt.gfx.nodepath.node():
            return
        curr_time = round(globalClock.getFrameTime(), 2)
        eng.log_mgr.log('collision with %s %s' % (obj_name, curr_time))
        if obj_name.startswith('Respawn'):
            self.__process_respawn()

    def reset_car(self):
        self.mdt.gfx.nodepath.set_pos(self.mdt.logic.start_pos)
        self.mdt.gfx.nodepath.set_hpr(self.mdt.logic.start_pos_hpr)
        wheels = self.mdt.phys.vehicle.get_wheels()
        map(lambda whl: whl.set_rotation(0), wheels)

    def on_frame(self):
        input_dct = self._get_input()
        if self.mdt.race.track.fsm.getCurrentOrNextState() != 'Race':
            input_dct = {key: False for key in input_dct}
            self.reset_car()
        self.mdt.logic.update(input_dct)
        if self.mdt.logic.is_upside_down:
            self.mdt.gfx.nodepath.setR(0)
        car_pos = self.mdt.gfx.nodepath.get_pos()
        top, bottom = (car_pos.x, car_pos.y, 100), (car_pos.x, car_pos.y, -100)
        result = eng.phys.world_phys.rayTestAll(top, bottom)
        hits = result.getHits()
        for hit in [hit for hit in hits if 'Road' in hit.getNode().getName()]:
            self.mdt.logic.last_contact_pos = self.mdt.gfx.nodepath.getPos()
        self.mdt.phys.update_terrain()

    def destroy(self):
        Event.destroy(self)
        eng.phys.detach(self.on_collision)
        eng.event.detach(self.on_frame)


class NetMsgs(object):
    game_packet = 0
    player_info = 1
    end_race_player = 2
    end_race = 3


class _PlayerEvent(_Event):

    def __init__(self, mdt):
        _Event.__init__(self, mdt)
        self.accept('f11', self.mdt.gui.toggle)
        if eng.server.is_active:
            self.server_info = {}
        self.last_sent = globalClock.getFrameTime()

    def eval_register(self):
        # make _PlayerEventServer, _PlayerEventClient
        if eng.server.is_active:
            eng.server.register_cb(self.process_srv)
        elif eng.client.is_active:
            eng.client.register_cb(self.process_client)

    def __on_frame_server(self):
        pos = self.mdt.gfx.nodepath.getPos()
        hpr = self.mdt.gfx.nodepath.getHpr()
        velocity = self.mdt.phys.vehicle.getChassis().getLinearVelocity()
        self.server_info['server'] = (pos, hpr, velocity)
        for car in [car for car in game.cars if car.ai_cls == _Ai]:
            pos = car.gfx.nodepath.getPos()
            hpr = car.gfx.nodepath.getHpr()
            velocity = car.phys.vehicle.getChassis().getLinearVelocity()
            self.server_info[car] = (pos, hpr, velocity)
        if globalClock.getFrameTime() - self.last_sent > .2:
            eng.server.send(self.__prepare_game_packet())
            self.last_sent = globalClock.getFrameTime()

    def __on_frame_client(self):
        pos = self.mdt.gfx.nodepath.getPos()
        hpr = self.mdt.gfx.nodepath.getHpr()
        velocity = self.mdt.phys.vehicle.getChassis().getLinearVelocity()
        packet = list(chain([NetMsgs.player_info], pos, hpr, velocity))
        if globalClock.getFrameTime() - self.last_sent > .2:
            eng.client.send(packet)
            self.last_sent = globalClock.getFrameTime()

    def on_frame(self):
        _Event.on_frame(self)
        self.mdt.logic.camera.update_cam()
        self.mdt.audio.update(self._get_input())
        if eng.server.is_active:
            self.__on_frame_server()
        if eng.client.is_active:
            self.__on_frame_client()

    @staticmethod
    def __prepare_game_packet():
        #should be done by race
        packet = [NetMsgs.game_packet]
        for car in [game.player_car] + game.cars:
            name = car.gfx.path
            pos = car.gfx.nodepath.getPos()
            hpr = car.gfx.nodepath.getHpr()
            velocity = car.phys.vehicle.getChassis().getLinearVelocity()
            packet += chain([name], pos, hpr, velocity)
        return packet

    def __process_wall(self):
        eng.audio.play(self.mdt.audio.crash_sfx)
        args = .1, lambda tsk: self.mdt.gfx.crash_sfx(), 'crash sfx'
        taskMgr.doMethodLater(*args)

    def __process_nonstart_goals(self, lap_number, laps):
        fwd = self.mdt.logic.direction > 0 and self.mdt.phys.speed > 0
        back = self.mdt.logic.direction < 0 and self.mdt.phys.speed < 0
        if fwd or back:
            self.mdt.gui.lap_txt.setText(str(min(laps, lap_number))+'/'+str(laps))
            eng.audio.play(self.mdt.audio.lap_sfx)
        else:
            self.mdt.gui.lap_txt.setText(str(lap_number - 1)+'/'+str(laps))

    def __process_end_goal(self):
        if eng.server.is_active:
            eng.server.send([NetMsgs.end_race])
        elif eng.client.is_active:
            eng.client.send([NetMsgs.end_race_player])
        self.notify('on_end_race')

    def __process_goal(self):
        if self.mdt.gui.time_txt.getText():
            lap_time = float(self.mdt.gui.time_txt.getText())
            self.mdt.logic.lap_times += [lap_time]
        lap_number = 1 + len(self.mdt.logic.lap_times)
        not_started = self.mdt.logic.last_time_start
        best_txt = self.mdt.gui.best_txt
        not_text = not best_txt.getText()
        is_best_txt = not_text or float(best_txt.getText()) > lap_time
        if not_started and (not_text or is_best_txt):
            self.mdt.gui.best_txt.setText(self.mdt.gui.time_txt.getText())
        laps = self.mdt.laps
        if self.mdt.logic.last_time_start:
            self.__process_nonstart_goals(lap_number, laps)
        if lap_number == laps + 1:
            self.__process_end_goal()
        self.mdt.logic.last_time_start = globalClock.getFrameTime()

    def on_collision(self, obj, obj_name):
        _Event.on_collision(self, obj, obj_name)
        if obj != self.mdt.gfx.nodepath.node():
            return
        if obj_name.startswith('Wall'):
            self.__process_wall()
        if any(obj_name.startswith(s) for s in ['Road', 'Offroad']):
            eng.audio.play(self.mdt.audio.landing_sfx)
        if obj_name.startswith('Goal'):
            self.__process_goal()

    def __process_player_info(self, data_lst, sender):
        from .car import NetworkCar
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
            # move into race
            game.track.fsm.demand('Results')
            game.track.gui.show_results()

    @staticmethod
    def __process_game_packet(data_lst):
        # into race
        from .car import NetworkCar
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
            if game.track.fsm.getCurrentOrNextState() != 'Results':
                game.track.fsm.demand('Results')
                game.track.gui.show_results()

    def _get_input(self):
        return {
            'forward': inputState.isSet('forward'),
            'left': inputState.isSet('left'),
            'reverse': inputState.isSet('reverse'),
            'right': inputState.isSet('right')}


class _NetworkEvent(_Event):

    def _get_input(self):
        return {
            'forward': False,
            'left': False,
            'reverse': False,
            'right': False}


class _AiEvent(_Event):

    def _get_input(self):
        return self.mdt.ai.get_input()
