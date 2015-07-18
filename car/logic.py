from ya2.gameobject import Logic
from panda3d.core import Vec3, Vec2, deg2Rad
import math


class _Logic(Logic):
    '''This class manages the events of the Car class.'''

    def __init__(self, mdt):
        Logic.__init__(self, mdt)
        self.__steering = 0  # degrees
        self.last_time_start = 0
        self.last_roll_ok_time = None
        self.lap_times = []

    def update(self, input_dct):
        '''This callback method is invoked on each frame.'''
        eng_frc = brake_frc = 0
        d_t = globalClock.getDt()
        steering_inc = d_t * self.mdt.phys.steering_inc
        steering_dec = d_t * self.mdt.phys.steering_dec

        speed_ratio = min(1.0, self.mdt.phys.speed / self.mdt.phys.max_speed)
        steering_range = self.mdt.phys.steering_min_speed - self.mdt.phys.steering_max_speed
        steering_clamp = self.mdt.phys.steering_min_speed - speed_ratio * steering_range

        if input_dct['forward']:
            eng_frc = self.mdt.phys.engine_acc_frc if self.mdt.phys.speed < self.mdt.phys.max_speed else 0
            brake_frc = 0

        if input_dct['reverse']:
            eng_frc = self.mdt.phys.engine_dec_frc if self.mdt.phys.speed < .05 else 0
            brake_frc = self.mdt.phys.brake_frc

        if input_dct['left']:
            self.__steering += steering_inc
            self.__steering = min(self.__steering, steering_clamp)

        if input_dct['right']:
            self.__steering -= steering_inc
            self.__steering = max(self.__steering, -steering_clamp)

        if not input_dct['left'] and not input_dct['right']:
            if abs(self.__steering) <= steering_dec:
                self.__steering = 0
            else:
                steering_sign = (-1 if self.__steering > 0 else 1)
                self.__steering += steering_sign * steering_dec

        self.mdt.phys.set_forces(eng_frc, brake_frc, self.__steering)
        self.mdt.gui.speed_txt.setText(str(round(self.mdt.phys.speed, 2)))
        if not self.mdt.event.has_just_started:
            self.mdt.gui.time_txt.setText(str(round(
                globalClock.getFrameTime() - self.last_time_start, 2)))
        self.__update_roll_info()
        self.__update_wp()

    def __update_roll_info(self):
        if -45 <= self.mdt.gfx.nodepath.getR() < 45:
            self.last_roll_ok_time = globalClock.getFrameTime()

    def __update_wp(self):
        car_np = self.mdt.gfx.nodepath
        waypoints = game.track.gfx.waypoints
        distances = [car_np.getDistance(wp) for wp in waypoints]
        curr_wp_idx = distances.index(min(distances))
        curr_wp = waypoints[curr_wp_idx]
        prev_wp = waypoints[(curr_wp_idx - 1) % len(waypoints)]
        next_wp = waypoints[(curr_wp_idx + 1) % len(waypoints)]
        curr_vec = Vec2(car_np.getPos(curr_wp).xy)
        curr_vec.normalize()
        prev_vec = Vec2(car_np.getPos(prev_wp).xy)
        prev_vec.normalize()
        next_vec = Vec2(car_np.getPos(next_wp).xy)
        next_vec.normalize()
        prev_angle = prev_vec.signedAngleDeg(curr_vec)
        next_angle = next_vec.signedAngleDeg(curr_vec)

        if abs(prev_angle) > abs(next_angle):
            start_wp = prev_wp
            end_wp = curr_wp
        else:
            start_wp = curr_wp
            end_wp = next_wp
        wp_vec = Vec3(end_wp.getPos(start_wp).xy, 1)
        wp_vec.normalize()

        car_rad = deg2Rad(car_np.getH())
        car_vec = Vec3(-math.sin(car_rad), math.cos(car_rad), 1)
        car_vec.normalize()

        prod = car_vec.dot(wp_vec)
        game.track.gui.way_txt.setText(_('wrong way') if prod < -.6 else '')

    @property
    def is_upside_down(self):
        return globalClock.getFrameTime() - self.last_roll_ok_time > 5.0
