from direct.showbase.InputStateGlobal import inputState
from ya2.gameobject import Event
from panda3d.core import AudioSound, Vec3, Vec2


class _Event(Event):
    '''This class manages the events of the Car class.'''

    def __init__(self, mdt):
        Event.__init__(self, mdt)
        self.has_just_started = True
        self.accept('f11', self.mdt.gui.toggle)
        self.accept('on_frame', self.__on_frame)
        self.accept('on_collision', self.__on_collision)
        label_events = [('forward', 'arrow_up'),
                        ('left', 'arrow_left'),
                        ('reverse', 'z'),
                        ('reverse', 'arrow_down'),
                        ('right', 'arrow_right')]
        map(lambda (lab, evt): inputState.watchWithModifiers(lab, evt),
            label_events)

    def __on_collision(self, obj_name):
        print 'collision with %s %s' % (obj_name, round(globalClock.getFrameTime(), 2))
        if obj_name == 'Wall':
            if self.mdt.audio.crash_sfx.status() != AudioSound.PLAYING:
                self.mdt.audio.crash_sfx.play()
            taskMgr.doMethodLater(.1, self.__crash_sfx, 'crash sfx', [self.mdt.phys.speed, self.mdt.phys.speed_ratio])
        if obj_name in ['Road', 'Offroad']:
            if self.mdt.audio.landing_sfx.status() != AudioSound.PLAYING:
                self.mdt.audio.landing_sfx.play()
        if obj_name in ['Respawn']:
            last_pos = self.mdt.logic.last_contact_pos
            start_wp_n, end_wp_n = self.mdt.logic.current_wp
            start_wp, end_wp = start_wp_n.get_pos(), end_wp_n.get_pos()
            # A + dot(AP,AB) / dot(AB,AB) * AB
            point_vec = Vec3(last_pos.x - start_wp.x,
                             last_pos.y - start_wp.y,
                             last_pos.z - start_wp.z)
            wp_vec = Vec3(end_wp.x - start_wp.x,
                          end_wp.y - start_wp.y,
                          end_wp.z - start_wp.z)
            dot_point = point_vec.dot(wp_vec)
            dot_wp = wp_vec.dot(wp_vec)
            delta = wp_vec * (dot_point / dot_wp)
            new_pos = start_wp + delta
            self.mdt.gfx.nodepath.setPos(new_pos.x, new_pos.y, new_pos.z + 2)

            wp_vec = Vec3(end_wp_n.getPos(start_wp_n).xy, 0)
            wp_vec.normalize()
            or_h = (wp_vec.xy).signedAngleDeg(Vec2(0, 1))
            self.mdt.gfx.nodepath.setHpr(-or_h, 0, 0)
            self.mdt.gfx.nodepath.node().setLinearVelocity(0)
            self.mdt.gfx.nodepath.node().setAngularVelocity(0)
        if obj_name == 'Goal':
            lap_number = int(self.mdt.gui.lap_txt.getText().split('/')[0])
            if self.mdt.gui.time_txt.getText():
                lap_time = float(self.mdt.gui.time_txt.getText())
                self.mdt.logic.lap_times += [lap_time]
            if not self.has_just_started and (
                    not self.mdt.gui.best_txt.getText() or
                    float(self.mdt.gui.best_txt.getText()) > lap_time):
                self.mdt.gui.best_txt.setText(self.mdt.gui.time_txt.getText())
            self.mdt.logic.last_time_start = globalClock.getFrameTime()
            if not self.has_just_started:
                fwd = self.mdt.logic.direction > 0 and self.mdt.phys.speed > 0
                back = self.mdt.logic.direction < 0 and self.mdt.phys.speed < 0
                if fwd or back:
                    self.mdt.gui.lap_txt.setText(str(lap_number + 1)+'/3')
                    if self.mdt.audio.lap_sfx.status() != AudioSound.PLAYING:
                        self.mdt.audio.lap_sfx.play()
                else:
                    self.mdt.gui.lap_txt.setText(str(lap_number - 1)+'/3')
            self.has_just_started = False
            if lap_number >= 3:
                game.track.fsm.demand('Results')
                game.track.gui.show_results()
        #if evt.obj_name == 'Slow':

    def __crash_sfx(self, speed, speed_ratio):
        print self.mdt.phys.speed, speed
        if abs(self.mdt.phys.speed) < abs(speed / 2.0) and speed_ratio > .5:
            self.mdt.audio.crash_high_speed_sfx.play()
            eng.particle('assets/particles/sparks.ptf', self.mdt.gfx.nodepath,
                         eng.render, (0, 1.2, .75), .8)

    def __on_frame(self):
        '''This callback method is invoked on each frame.'''
        input_dct = {
            'forward': inputState.isSet('forward'),
            'left': inputState.isSet('left'),
            'reverse': inputState.isSet('reverse'),
            'right': inputState.isSet('right')}
        if game.track.fsm.getCurrentOrNextState() != 'Race':
            input_dct = {key: False for key in input_dct}
            self.mdt.gfx.nodepath.set_pos(self.mdt.logic.start_pos)
            self.mdt.gfx.nodepath.set_hpr(self.mdt.logic.start_pos_hpr)
            wheels = self.mdt.phys.vehicle.get_wheels()
            map(lambda whl: whl.set_rotation(0), wheels)
        self.mdt.logic.update(input_dct)
        self.mdt.audio.update(input_dct)
        self.mdt.logic.update_cam()
        if self.mdt.logic.is_upside_down:
            self.mdt.gfx.nodepath.setR(0)
        car_pos = self.mdt.gfx.nodepath.get_pos()
        top = (car_pos.x, car_pos.y, 100)
        bottom = (car_pos.x, car_pos.y, -100)
        result = eng.world_phys.rayTestAll(top, bottom)
        for hit in result.getHits():
            if 'Road' in hit.getNode().getName():
                self.mdt.logic.last_contact_pos = self.mdt.gfx.nodepath.getPos()
