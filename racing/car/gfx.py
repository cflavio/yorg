from racing.game.gameobject import Gfx
from panda3d.bullet import BulletRigidBodyNode


class _Gfx(Gfx):

    def __init__(self, mdt, path):
        self.rear_right_wheel_np = None
        self.chassis_np = None
        self.front_left_wheel_np = None
        self.front_right_wheel_np = None
        self.rear_left_wheel_np = None
        self.path = path
        vehicle_node = BulletRigidBodyNode('Vehicle')
        self.nodepath = eng.gfx.world_np.attachNewNode(vehicle_node)
        Gfx.__init__(self, mdt)

    def async_build(self):
        loader.loadModel(self.path + '/car', callback=self.load_wheels)

    def reparent(self):
        self.chassis_np.reparentTo(self.nodepath)
        self.chassis_np.setDepthOffset(-2)
        for wheel in [self.front_right_wheel_np, self.front_left_wheel_np,
                      self.rear_right_wheel_np, self.rear_left_wheel_np]:
            wheel.reparentTo(eng.gfx.world_np)

    def load_wheels(self, chassis_model):
        self.chassis_np = chassis_model
        load = eng.base.loader.loadModel
        self.front_right_wheel_np = load(self.path + '/frontwheel')
        self.front_left_wheel_np = load(self.path + '/frontwheel')
        self.rear_right_wheel_np = load(self.path + '/rearwheel')
        self.rear_left_wheel_np = load(self.path + '/rearwheel')
        Gfx._end_async(self)

    def crash_sfx(self):
        eng.log_mgr.log('crash speed %s' % self.mdt.phys.speed)
        speed, speed_ratio = self.mdt.phys.speed, self.mdt.phys.speed_ratio
        if abs(self.mdt.phys.speed) >= abs(speed / 2.0) or speed_ratio < .5:
            return
        self.mdt.audio.crash_high_speed_sfx.play()
        part_path = 'assets/particles/sparks.ptf'
        node = self.mdt.gfx.nodepath
        eng.gfx.particle(part_path, node, eng.render, (0, 1.2, .75), .8)

    def destroy(self):
        meshes = [
            self.nodepath, self.chassis_np, self.front_right_wheel_np,
            self.front_left_wheel_np, self.rear_right_wheel_np,
            self.rear_right_wheel_np]
        map(lambda mesh: mesh.removeNode(), meshes)
        Gfx.destroy(self)
