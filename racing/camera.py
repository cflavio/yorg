from panda3d.core import Vec3


class Camera(object):

    cam_speed = 50
    cam_dist_min = 12
    cam_dist_max = 18
    cam_z_max = 5
    cam_z_min = 3
    look_dist_min = 2
    look_dist_max = 6
    look_z_max = 2
    look_z_min = 0

    def __init__(self, mdt):
        self.mdt = mdt
        self.tgt_y = None
        self.tgt_x = None
        self.tgt_look_x = None
        self.tgt_z = None
        self.tgt_look_z = None
        self.tgt_look_y = None

    def __cam_cond(self, curr_pos, curr_cam_fact):
        closest = self.get_closest(curr_pos)
        if closest:
            cls_s = closest.getNode().getName()
        if closest and cls_s not in ['Vehicle', 'Goal'] and curr_cam_fact > .1:
            return closest

    def update_cam(self):
        speed_ratio = self.mdt.phys.speed_ratio
        cam_dist_diff = self.cam_dist_max - self.cam_dist_min
        look_dist_diff = self.look_dist_max - self.look_dist_min
        cam_z_diff = self.cam_z_max - self.cam_z_min
        look_z_diff = self.look_z_max - self.look_z_min
        #car_np = self.mdt.gfx.nodepath
        #car_rad = deg2Rad(car_np.getH())
        #car_vec = Vec3(-math.sin(car_rad), math.cos(car_rad), 1)
        #car_vec.normalize()

        nodepath = self.mdt.gfx.nodepath
        fwd_vec = eng.base.render.getRelativeVector(nodepath, Vec3(0, 1, 0))
        fwd_vec.normalize()

        car_pos = self.mdt.gfx.nodepath.getPos()
        #cam_vec = -car_vec * (cam_dist_min + cam_dist_diff * speed_ratio)
        #tgt_vec = car_vec * (look_dist_min + look_dist_diff * speed_ratio)
        cam_vec = -fwd_vec * (self.cam_dist_min + cam_dist_diff * speed_ratio)
        tgt_vec = fwd_vec * (self.look_dist_min + look_dist_diff * speed_ratio)
        delta_pos_z = self.cam_z_max - cam_z_diff * speed_ratio
        delta_cam_z = self.look_z_min + look_z_diff * speed_ratio

        curr_pos = car_pos + cam_vec + (0, 0, delta_pos_z)
        curr_cam_fact = self.cam_dist_min + cam_dist_diff * speed_ratio

        curr_hit = self.__cam_cond(curr_pos, curr_cam_fact)
        if curr_hit:
            hit_pos = curr_hit.getHitPos()
            cam_vec = hit_pos - car_pos

        #game.track.gui.debug_txt.setText(
        #    curr_hit.getNode().getName() if curr_hit else '')

        self.tgt_x = car_pos.x + cam_vec.x
        self.tgt_y = car_pos.y + cam_vec.y
        self.tgt_z = car_pos.z + cam_vec.z + delta_pos_z

        self.tgt_look_x = car_pos.x + tgt_vec.x
        self.tgt_look_y = car_pos.y + tgt_vec.y
        self.tgt_look_z = car_pos.z + tgt_vec.z

        curr_incr = self.cam_speed * globalClock.getDt()

        def new_pos(cam_pos, tgt):
            if abs(cam_pos - tgt) <= curr_incr:
                return tgt
            else:
                return cam_pos + (1 if tgt > cam_pos else -1) * curr_incr
        new_x = new_pos(eng.base.camera.getX(), self.tgt_x)
        new_y = new_pos(eng.base.camera.getY(), self.tgt_y)
        new_z = new_pos(eng.base.camera.getZ(), self.tgt_z)

        # overwrite camera's position to set the physics
        #new_x = car_pos.x + 10
        #new_y = car_pos.y - 5
        #new_z = car_pos.z + 5

        if not self.mdt.logic.is_rolling:
            eng.base.camera.setPos(new_x, new_y, new_z)
        look_z = self.tgt_look_z + delta_cam_z
        eng.base.camera.look_at(self.tgt_look_x, self.tgt_look_y, look_z)

    def get_closest(self, pos, tgt=None):
        tgt = tgt or self.mdt.gfx.nodepath.getPos()
        result = eng.phys.world_phys.rayTestClosest(pos, tgt)
        if result.hasHit():
            return result

    @property
    def camera(self):
        return eng.base.camera
