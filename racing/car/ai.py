from racing.game.gameobject import Ai
from panda3d.core import Vec3, Vec2, Point3, Mat4


class _Ai(Ai):

    @property
    def current_target(self):
        curr_wp = self.mdt.logic.current_wp[1]
        waypoints = game.track.phys.waypoints
        next_wp_idx = (waypoints.keys().index(curr_wp) + 1) % len(waypoints)
        dist_vec = curr_wp.get_pos() - self.mdt.gfx.nodepath.get_pos()
        distance = dist_vec.length()
        return curr_wp if distance > 15 else waypoints.keys()[next_wp_idx]

    @property
    def car_vec(self):
        car_vec = self.mdt.logic.car_vec.xy
        car_vec.normalize()
        return car_vec

    @property
    def curr_dot_prod(self):
        curr_tgt_pos = self.current_target.get_pos().xy
        curr_pos = self.mdt.gfx.nodepath.get_pos().xy
        tgt_vec = Vec2(curr_tgt_pos - curr_pos)
        tgt_vec.normalize()
        return self.car_vec.dot(tgt_vec)

    @property
    def brake(self):
        if self.mdt.phys.speed < 40:
            return False
        return self.curr_dot_prod < .4

    @property
    def acceleration(self):
        if self.mdt.phys.speed < 40:
            return True
        grounds = self.mdt.phys.ground_names
        if not all(name.startswith('Road') for name in grounds):
            return False
        return self.curr_dot_prod > .8

    @staticmethod
    def ground_name(pos):
        top, bottom = pos + (0, 0, 1), pos + (0, 0, -1)
        result = eng.phys.world_phys.rayTestClosest(top, bottom)
        ground = result.get_node()
        return ground.get_name() if ground else ''

    def lookahead_ground(self, dist, deg):
        lookahed_vec = self.car_vec * dist
        #TODO: port this algorithm to 3D
        rot_mat = Mat4()
        rot_mat.setRotateMat(deg, (0, 0, 1))
        lookahead_rot = rot_mat.xformVec((lookahed_vec.x, lookahed_vec.y, 0))
        lookahead_pt = Point3(lookahead_rot.x, lookahead_rot.y, 0)
        lookahead_pos = self.mdt.gfx.nodepath.get_pos() + lookahead_pt
        return self.ground_name(lookahead_pos)

    @property
    def left_right(self):
        fwd_ground = self.lookahead_ground(30, 0)
        right_ground = self.lookahead_ground(30, -20)
        left_ground = self.lookahead_ground(30, 20)
        fwd_ground2 = self.lookahead_ground(10, 0)
        right_ground2 = self.lookahead_ground(10, -30)
        left_ground2 = self.lookahead_ground(10, 30)
        if self.curr_dot_prod > 0 and not fwd_ground.startswith('Road'):
            if left_ground.startswith('Road'):
                return True, False
            elif right_ground.startswith('Road'):
                return False, True
        if self.curr_dot_prod > 0 and not fwd_ground2.startswith('Road'):
            if left_ground2.startswith('Road'):
                return True, False
            elif right_ground2.startswith('Road'):
                return False, True
        if abs(self.curr_dot_prod) > .9:
            return False, False
        curr_tgt_pos = self.current_target.get_pos().xy
        curr_pos = self.mdt.gfx.nodepath.get_pos().xy
        tgt = Vec2(curr_tgt_pos - curr_pos)
        car_vec = self.car_vec
        cross = Vec3(tgt.x, tgt.y, 0).cross(Vec3(car_vec.x, car_vec.y, 0))
        dot_res = cross.dot(Vec3(0, 0, 1))
        return dot_res < 0, dot_res >= 0

    def get_input(self):
        brake = self.brake
        acceleration = False if brake else self.acceleration
        left, right = self.left_right
        return {'forward': acceleration, 'left': left, 'reverse': brake,
                'right': right}
