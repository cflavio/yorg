from direct.showbase.InputStateGlobal import inputState
from racing.game.gameobject import Event
from panda3d.core import AudioSound, Vec3, Vec2
from ai import _Ai
from direct.interval.LerpInterval import LerpPosInterval, LerpHprInterval
from racing.game.option import OptionMgr


class _Event(Event):
    '''This class manages the events of the Car class.'''

    def __init__(self, mdt):
        Event.__init__(self, mdt)
        self.has_just_started = True
        self.accept('on_frame', self._on_frame)
        self.accept('on_collision', self._on_collision)
        label_events = [('forward', 'arrow_up'),
                        ('left', 'arrow_left'),
                        ('reverse', 'z'),
                        ('reverse', 'arrow_down'),
                        ('right', 'arrow_right')]
        map(lambda (lab, evt): inputState.watchWithModifiers(lab, evt),
            label_events)

    def _on_collision(self, obj, obj_name):
        if obj != self.mdt.gfx.nodepath.node():
            return
        print 'collision with %s %s' % (obj_name, round(globalClock.getFrameTime(), 2))
        if obj_name.startswith('Respawn'):
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

    def _get_input(self):
        if self.mdt.ai.__class__ == _Ai:
            return self.mdt.ai.get_input()
        elif self.__class__ == _NetworkEvent:
            return {
                'forward': False,
                'left': False,
                'reverse': False,
                'right': False}
        else:
            return {
                'forward': inputState.isSet('forward'),
                'left': inputState.isSet('left'),
                'reverse': inputState.isSet('reverse'),
                'right': inputState.isSet('right')}

    def reset_car(self):
        self.mdt.gfx.nodepath.set_pos(self.mdt.logic.start_pos)
        self.mdt.gfx.nodepath.set_hpr(self.mdt.logic.start_pos_hpr)
        wheels = self.mdt.phys.vehicle.get_wheels()
        map(lambda whl: whl.set_rotation(0), wheels)

    def _on_frame(self):
        '''This callback method is invoked on each frame.'''
        input_dct = self._get_input()
        if game.track.fsm.getCurrentOrNextState() != 'Race':
            input_dct = {key: False for key in input_dct}
            self.reset_car()
        self.mdt.logic.update(input_dct)
        if self.mdt.logic.is_upside_down:
            self.mdt.gfx.nodepath.setR(0)
        car_pos = self.mdt.gfx.nodepath.get_pos()
        top = (car_pos.x, car_pos.y, 100)
        bottom = (car_pos.x, car_pos.y, -100)
        result = eng.phys_mgr.world_phys.rayTestAll(top, bottom)
        for hit in result.getHits():
            if 'Road' in hit.getNode().getName():
                self.mdt.logic.last_contact_pos = self.mdt.gfx.nodepath.getPos()
        self.mdt.phys.update_terrain()


class NetMsgs:

    game_packet = 0
    player_info = 1
    end_race_player = 2
    end_race = 3


class _PlayerEvent(_Event):

    def __init__(self, mdt):
        _Event.__init__(self, mdt)
        self.accept('f11', self.mdt.gui.toggle)
        if hasattr(game.logic, 'srv') and game.logic.srv.is_active:
            self.server_info = {}
        self.last_sent = globalClock.getFrameTime()

    def eval_register(self):
        if hasattr(game.logic, 'srv') and game.logic.srv.is_active:
            game.logic.srv.register_cb(self.process_srv)
        elif hasattr(game.logic, 'client') and game.logic.client.is_active:
            game.logic.client.register_cb(self.process_client)

    def _on_frame(self):
        '''This callback method is invoked on each frame.'''
        _Event._on_frame(self)
        self.mdt.logic.update_cam()
        self.mdt.audio.update(self._get_input())
        if hasattr(game.logic, 'srv') and game.logic.srv.is_active:
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
                game.logic.srv.send(self.__prepare_game_packet())
                self.last_sent = globalClock.getFrameTime()
        if hasattr(game.logic, 'client') and game.logic.client.is_active:
            pos = self.mdt.gfx.nodepath.getPos()
            hpr = self.mdt.gfx.nodepath.getHpr()
            velocity = self.mdt.phys.vehicle.getChassis().getLinearVelocity()
            from itertools import chain
            packet = list(chain([NetMsgs.player_info], pos, hpr, velocity))
            if globalClock.getFrameTime() - self.last_sent > .2:
                game.logic.client.send(packet)
                self.last_sent = globalClock.getFrameTime()

    def __prepare_game_packet(self):
        packet = [NetMsgs.game_packet]
        for car in [game.player_car] + game.cars:
            name = car.gfx.path
            pos = car.gfx.nodepath.getPos()
            hpr = car.gfx.nodepath.getHpr()
            velocity = car.phys.vehicle.getChassis().getLinearVelocity()
            from itertools import chain
            packet += chain([name], pos, hpr, velocity)
        return packet

    def __crash_sfx(self, speed, speed_ratio):
        print 'crash speed', self.mdt.phys.speed, speed
        if abs(self.mdt.phys.speed) < abs(speed / 2.0) and speed_ratio > .5:
            self.mdt.audio.crash_high_speed_sfx.play()
            eng.particle('assets/particles/sparks.ptf', self.mdt.gfx.nodepath,
                         eng.render, (0, 1.2, .75), .8)

    def _on_collision(self, obj, obj_name):
        _Event._on_collision(self, obj, obj_name)
        if obj != self.mdt.gfx.nodepath.node():
            return
        if obj_name.startswith('Wall'):
            if self.mdt.audio.crash_sfx.status() != AudioSound.PLAYING:
                self.mdt.audio.crash_sfx.play()
            taskMgr.doMethodLater(.1, self.__crash_sfx, 'crash sfx', [self.mdt.phys.speed, self.mdt.phys.speed_ratio])
        if any(obj_name.startswith(s) for s in ['Road', 'Offroad']):
            if self.mdt.audio.landing_sfx.status() != AudioSound.PLAYING:
                self.mdt.audio.landing_sfx.play()
        if obj_name.startswith('Goal'):
            lap_number = int(self.mdt.gui.lap_txt.getText().split('/')[0])
            if self.mdt.gui.time_txt.getText():
                lap_time = float(self.mdt.gui.time_txt.getText())
                self.mdt.logic.lap_times += [lap_time]
            if not self.has_just_started and (
                    not self.mdt.gui.best_txt.getText() or
                    float(self.mdt.gui.best_txt.getText()) > lap_time):
                self.mdt.gui.best_txt.setText(self.mdt.gui.time_txt.getText())
            self.mdt.logic.last_time_start = globalClock.getFrameTime()
            laps = OptionMgr.get_options()['laps']
            if not self.has_just_started:
                fwd = self.mdt.logic.direction > 0 and self.mdt.phys.speed > 0
                back = self.mdt.logic.direction < 0 and self.mdt.phys.speed < 0
                if fwd or back:
                    self.mdt.gui.lap_txt.setText(str(lap_number + 1)+'/'+str(laps))
                    if self.mdt.audio.lap_sfx.status() != AudioSound.PLAYING:
                        self.mdt.audio.lap_sfx.play()
                else:
                    self.mdt.gui.lap_txt.setText(str(lap_number - 1)+'/'+str(laps))
            self.has_just_started = False
            if int(self.mdt.gui.lap_txt.getText().split('/')[0]) > laps:
                if hasattr(game.logic, 'srv') and game.logic.srv.is_active:
                    game.logic.srv.send([NetMsgs.end_race])
                elif hasattr(game.logic, 'client') and game.logic.client.is_active:
                    game.logic.client.send([NetMsgs.end_race_player])
                #TODO: compute the ranking
                game.track.race_ranking = {
                    'kronos': 0,
                    'themis': 0,
                    'diones': 0}
                game.track.fsm.demand('Results')
                game.track.gui.show_results()

    def process_srv(self, data_lst, sender):
        from car import NetworkCar
        if data_lst[0] == NetMsgs.player_info:
            pos = (data_lst[1], data_lst[2], data_lst[3])
            hpr = (data_lst[4], data_lst[5], data_lst[6])
            velocity = (data_lst[7], data_lst[8], data_lst[9])
            self.server_info[sender] = (pos, hpr, velocity)
            car_name = game.logic.srv.car_mapping[sender]
            for car in [car for car in game.cars if car.__class__ == NetworkCar]:
                if car_name in car.gfx.path:
                    LerpPosInterval(car.gfx.nodepath, .2, pos).start()
                    LerpHprInterval(car.gfx.nodepath, .2, hpr).start()
        if data_lst[0] == NetMsgs.end_race_player:
            game.logic.srv.send([NetMsgs.end_race])
            game.track.fsm.demand('Results')
            game.track.gui.show_results()

    def process_client(self, data_lst, sender):
        from car import NetworkCar
        car_info = {}
        if data_lst[0] == NetMsgs.game_packet:
            for i in range(1, len(data_lst), 10):
                car_name = data_lst[i]
                car_pos = (data_lst[i + 1], data_lst[i + 2], data_lst[i + 3])
                car_hpr = (data_lst[i + 4], data_lst[i + 5], data_lst[i + 6])
                car_velocity = (data_lst[i + 7], data_lst[i + 8], data_lst[i + 9])
                for car in [car for car in game.cars if car.__class__ == NetworkCar]:
                    if car_name in car.gfx.path:
                        LerpPosInterval(car.gfx.nodepath, .2, car_pos).start()
                        LerpHprInterval(car.gfx.nodepath, .2, car_hpr).start()
        if data_lst[0] == NetMsgs.end_race:
            if game.track.fsm.getCurrentOrNextState() != 'Results':
                game.track.fsm.demand('Results')
                game.track.gui.show_results()


class _NetworkEvent(_Event):

    pass
