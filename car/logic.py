from ya2.gameobject import Logic
from panda3d.core import Vec3, Vec2, deg2Rad
import math


#camera constants
cam_speed = 25
cam_dist_min = 12
cam_dist_max = 16
cam_z_max = 4
cam_z_min = 3.2
look_z_max = 2.4
look_z_min = 2


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

        speed_ratio = self.mdt.phys.speed_ratio
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

    @property
    def direction(self):
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

        return car_vec.dot(wp_vec)

    def __update_wp(self):
        way_str = _('wrong way') if self.direction < -.6 else ''
        game.track.gui.way_txt.setText(way_str)

    def update_cam(self):
        cam_dist_diff = cam_dist_max - cam_dist_min
        cam_z_diff = cam_z_max - cam_z_min
        look_z_diff = look_z_max - look_z_min
        car_np = self.mdt.gfx.nodepath
        car_rad = deg2Rad(car_np.getH())
        car_vec = Vec3(-math.sin(car_rad), math.cos(car_rad), 1)
        car_vec.normalize()
        cam_vec = car_vec * (cam_dist_min + cam_dist_diff * self.mdt.phys.speed_ratio)
        car_pos = self.mdt.gfx.nodepath.getPos()
        delta_pos_z = cam_z_max - cam_z_diff * self.mdt.phys.speed_ratio
        delta_cam_z = look_z_min + look_z_diff * self.mdt.phys.speed_ratio
        self.tgt_x = car_pos.x - cam_vec.x
        self.tgt_y = car_pos.y - cam_vec.y
        self.tgt_z = car_pos.z + delta_pos_z
        curr_incr = cam_speed * globalClock.getDt()
        def new_pos(cam_pos, tgt):
            if abs(cam_pos - tgt) <= curr_incr:
                return tgt
            else:
                sign = 1 if tgt > cam_pos else -1
                return cam_pos + sign * curr_incr
        new_x = new_pos(eng.camera.getX(), self.tgt_x)
        new_y = new_pos(eng.camera.getY(), self.tgt_y)
        new_z = new_pos(eng.camera.getZ(), self.tgt_z)
        eng.camera.setPos(new_x, new_y, new_z)
        eng.camera.look_at(car_pos.x, car_pos.y, car_pos.z + delta_cam_z)

    @property
    def is_upside_down(self):
        return globalClock.getFrameTime() - self.last_roll_ok_time > 5.0
