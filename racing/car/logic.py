from racing.game.gameobject import Logic
from panda3d.core import Vec3, Vec2, deg2Rad
import math
from racing.camera import Camera


class CarLogic(Logic):

    react_time = .1

    def __init__(self, mdt):
        Logic.__init__(self, mdt)
        self.__steering = 0  # degrees
        self.last_time_start = 0
        self.last_roll_ok_time = globalClock.getFrameTime()
        self.last_roll_ko_time = globalClock.getFrameTime()
        self.lap_times = []
        self.start_left = None
        self.start_right = None
        self.camera = Camera(mdt)

    def update(self, input_dct):
        eng_frc = brake_frc = 0
        d_t = globalClock.getDt()
        f_t = globalClock.getFrameTime()
        phys = self.mdt.phys
        steering_inc = d_t * phys.steering_inc
        steering_dec = d_t * phys.steering_dec
        speed_ratio = phys.speed_ratio
        steering_range = phys.steering_min_speed - phys.steering_max_speed
        steering_clamp = phys.steering_min_speed - speed_ratio * steering_range
        if input_dct['forward'] and input_dct['reverse']:
            eng_frc = phys.engine_acc_frc
            brake_frc = phys.brake_frc
        if input_dct['forward'] and not input_dct['reverse']:
            eng_frc = phys.engine_acc_frc
            brake_frc = 0
        if input_dct['reverse'] and not input_dct['forward']:
            eng_frc = phys.engine_dec_frc if phys.speed < .05 else 0
            brake_frc = phys.brake_frc
        if not input_dct['forward'] and not input_dct['reverse']:
            brake_frc = phys.eng_brk_frc
        if input_dct['left']:
            if self.start_left is None:
                self.start_left = f_t
            mul = min(1, (f_t - self.start_left) / self.react_time)
            self.__steering += steering_inc * mul
            self.__steering = min(self.__steering, steering_clamp)
        else:
            self.start_left = None
        if input_dct['right']:
            if self.start_right is None:
                self.start_right = globalClock.getFrameTime()
            mul = min(1, (f_t - self.start_right) / self.react_time)
            self.__steering -= steering_inc * mul
            self.__steering = max(self.__steering, -steering_clamp)
        else:
            self.start_right = None
        if not input_dct['left'] and not input_dct['right']:
            if abs(self.__steering) <= steering_dec:
                self.__steering = 0
            else:
                steering_sign = (-1 if self.__steering > 0 else 1)
                self.__steering += steering_sign * steering_dec
        phys.set_forces(self.get_eng_frc(eng_frc), brake_frc, self.__steering)
        self.__update_roll_info()

    def get_eng_frc(self, eng_frc):
        curr_max_speed = self.mdt.phys.max_speed * self.mdt.phys.curr_speed_factor
        if self.mdt.phys.speed / curr_max_speed < .99:
            return eng_frc
        tot = .01 * curr_max_speed
        return eng_frc * min(1, (curr_max_speed - self.mdt.phys.speed) / tot)

    def __update_roll_info(self):
        if -45 <= self.mdt.gfx.nodepath.getR() < 45:
            self.last_roll_ok_time = globalClock.getFrameTime()
        else:
            self.last_roll_ko_time = globalClock.getFrameTime()

    def reset_car(self):
        self.mdt.gfx.nodepath.set_pos(self.mdt.logic.start_pos)
        self.mdt.gfx.nodepath.set_hpr(self.mdt.logic.start_pos_hpr)
        wheels = self.mdt.phys.vehicle.get_wheels()
        map(lambda whl: whl.set_rotation(0), wheels)

    def closest_wp(self, pos=None):
        if pos:
            node = render.attachNewNode('pos node')
            node.set_pos(pos)
        else:
            node = self.mdt.gfx.nodepath
        waypoints = game.track.phys.waypoints
        distances = [node.getDistance(wp) for wp in waypoints.keys()]
        curr_wp = waypoints.keys()[distances.index(min(distances))]
        may_prev = waypoints[curr_wp]
        distances = [self.pt_line_dst(node, w_p, curr_wp) for w_p in may_prev]
        prev_wp = may_prev[distances.index(min(distances))]
        may_succ = [w_p for w_p in waypoints if curr_wp in waypoints[w_p]]
        distances = [self.pt_line_dst(node, curr_wp, w_p) for w_p in may_succ]
        next_wp = may_succ[distances.index(min(distances))]
        curr_vec = Vec2(node.getPos(curr_wp).xy)
        curr_vec.normalize()
        prev_vec = Vec2(node.getPos(prev_wp).xy)
        prev_vec.normalize()
        next_vec = Vec2(node.getPos(next_wp).xy)
        next_vec.normalize()
        prev_angle = prev_vec.signedAngleDeg(curr_vec)
        next_angle = next_vec.signedAngleDeg(curr_vec)
        if abs(prev_angle) > abs(next_angle):
            start_wp, end_wp = prev_wp, curr_wp
        else:
            start_wp, end_wp = curr_wp, next_wp
        if pos:
            node.remove_node()
        return start_wp, end_wp

    @staticmethod
    def pt_line_dst(point, line_pt1, line_pt2):
        diff1 = line_pt2.get_pos() - line_pt1.get_pos()
        diff2 = line_pt1.get_pos() - point.get_pos()
        diff = abs(diff1.cross(diff2).length())
        return diff / abs(diff1.length())

    @property
    def car_vec(self):
        car_rad = deg2Rad(self.mdt.gfx.nodepath.getH())
        car_vec = Vec3(-math.sin(car_rad), math.cos(car_rad), 0)
        car_vec.normalize()
        return car_vec

    @property
    def direction(self):
        start_wp, end_wp = self.closest_wp()
        wp_vec = Vec3(end_wp.getPos(start_wp).xy, 0)
        wp_vec.normalize()
        return self.car_vec.dot(wp_vec)

    @property
    def is_upside_down(self):
        return globalClock.getFrameTime() - self.last_roll_ok_time > 5.0

    @property
    def is_rolling(self):
        return globalClock.getFrameTime() - self.last_roll_ko_time < 1.0

    def destroy(self):
        self.camera = None
        Logic.destroy(self)


class CarPlayerLogic(CarLogic):

    def update(self, input_dct):
        CarLogic.update(self, input_dct)
        if self.last_time_start:
            f_t = globalClock.getFrameTime()
            d_t = round(f_t - self.last_time_start, 2)
            self.mdt.gui.time_txt.setText(str(d_t))
        if self.last_time_start:
            self.mdt.gui.speed_txt.setText(str(round(self.mdt.phys.speed, 2)))
        self.__update_wp()

    def __update_wp(self):
        if game.track.phys.waypoints:
            way_str = _('wrong way') if self.direction < -.6 else ''
            self.notify('on_wrong_way', way_str)
