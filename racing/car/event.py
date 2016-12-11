from itertools import chain
from direct.showbase.InputStateGlobal import inputState
from racing.game.gameobject import Event
from racing.race.event import NetMsgs
from panda3d.core import Vec3, Vec2


class CarEvent(Event):

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

    def on_frame(self):
        input_dct = self._get_input()
        if game.fsm.race.fsm.getCurrentOrNextState() != 'Play':
            input_dct = {key: False for key in input_dct}
            self.mdt.logic.reset_car()
        self.mdt.logic.update(input_dct)
        if self.mdt.logic.is_upside_down:
            self.mdt.gfx.nodepath.setR(0)
        self.__update_contact_pos()
        self.mdt.phys.update_car_props()
        self.mdt.logic.update_waypoints()

    def __update_contact_pos(self):
        car_pos = self.mdt.gfx.nodepath.get_pos()
        top, bottom = (car_pos.x, car_pos.y, 100), (car_pos.x, car_pos.y, -100)
        result = eng.phys.world_phys.rayTestAll(top, bottom)
        hits = result.getHits()
        for hit in [hit for hit in hits if 'Road' in hit.getNode().getName()]:
            self.mdt.logic.last_contact_pos = self.mdt.gfx.nodepath.getPos()

    def destroy(self):
        Event.destroy(self)
        eng.phys.detach(self.on_collision)
        eng.event.detach(self.on_frame)


class CarPlayerEvent(CarEvent):

    def __init__(self, mdt):
        CarEvent.__init__(self, mdt)
        self.accept('f11', self.mdt.gui.toggle)

    def on_frame(self):
        CarEvent.on_frame(self)
        self.mdt.logic.camera.update_cam()
        self.mdt.audio.update(self._get_input())

    def __process_wall(self):
        eng.audio.play(self.mdt.audio.crash_sfx)
        args = .1, lambda tsk: self.mdt.gfx.crash_sfx(), 'crash sfx'
        taskMgr.doMethodLater(*args)

    def __process_nonstart_goals(self, lap_number, laps):
        curr_lap = min(laps, lap_number)
        self.mdt.gui.lap_txt.setText(str(curr_lap)+'/'+str(laps))
        eng.audio.play(self.mdt.audio.lap_sfx)

    def _process_end_goal(self):
        self.notify('on_end_race')

    def __process_goal(self):
        if self.mdt.logic.last_time_start and not self.mdt.logic.correct_lap:
            return
        self.mdt.logic.reset_waypoints()
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
        self.mdt.logic.last_time_start = globalClock.getFrameTime()
        if lap_number == laps + 1:
            self._process_end_goal()

    def on_collision(self, obj, obj_name):
        CarEvent.on_collision(self, obj, obj_name)
        if obj != self.mdt.gfx.nodepath.node():
            return
        if obj_name.startswith('Wall'):
            self.__process_wall()
        if any(obj_name.startswith(s) for s in ['Road', 'Offroad']):
            eng.audio.play(self.mdt.audio.landing_sfx)
        if obj_name.startswith('Goal'):
            self.__process_goal()

    def _get_input(self):
        return {
            'forward': inputState.isSet('forward'),
            'left': inputState.isSet('left'),
            'reverse': inputState.isSet('reverse'),
            'right': inputState.isSet('right')}


class CarPlayerEventServer(CarPlayerEvent):

    def __init__(self, mdt):
        _PlayerEvent.__init__(self, mdt)

    def _process_end_goal(self):
        eng.server.send([NetMsgs.end_race])
        _PlayerEvent._process_end_goal(self)


class CarPlayerEventClient(CarPlayerEvent):

    def __init__(self, mdt):
        CarPlayerEvent.__init__(self, mdt)
        self.last_sent = globalClock.getFrameTime()

    def on_frame(self):
        CarPlayerEvent.on_frame(self)
        pos = self.mdt.gfx.nodepath.getPos()
        hpr = self.mdt.gfx.nodepath.getHpr()
        velocity = self.mdt.phys.vehicle.getChassis().getLinearVelocity()
        packet = list(chain([NetMsgs.player_info], pos, hpr, velocity))
        if globalClock.getFrameTime() - self.last_sent > .2:
            eng.client.send(packet)
            self.last_sent = globalClock.getFrameTime()

    def _process_end_goal(self):
        eng.client.send([NetMsgs.end_race_player])
        CarPlayerEvent._process_end_goal(self)


class CarNetworkEvent(CarEvent):

    def _get_input(self):
        return {'forward': False, 'left': False, 'reverse': False,
                'right': False}


class CarAiEvent(CarEvent):

    def _get_input(self):
        return self.mdt.ai.get_input()
