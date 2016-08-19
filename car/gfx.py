from ya2.gameobject import Gfx
from panda3d.bullet import BulletRigidBodyNode


class _Gfx(Gfx):
    '''This class models the graphics component of a car.'''

    def __init__(self, mdt, path, cb):
        Gfx.__init__(self, mdt)
        self.path = path
        self.cb = cb
        vehicle_node = BulletRigidBodyNode('Vehicle')
        self.nodepath = eng.world_np.attachNewNode(vehicle_node)

        #eng.loader.loadModel(path + '/car', callback=self.load_wheels)  # it doesn't work
        chassis_model = eng.loader.loadModel(path + '/car')
        self.load_wheels(chassis_model)

    def reparent(self):
        self.chassis_np.reparentTo(self.nodepath)
        self.chassis_np.setDepthOffset(-2)
        self.front_right_wheel_np.reparentTo(eng.world_np)
        self.front_left_wheel_np.reparentTo(eng.world_np)
        self.rear_right_wheel_np.reparentTo(eng.world_np)
        self.rear_left_wheel_np.reparentTo(eng.world_np)

    def load_wheels(self, chassis_model):
        self.chassis_np = chassis_model
        try:
            self.front_right_wheel_np = eng.loader.loadModel(self.path + '/frontwheel')
            self.front_left_wheel_np = eng.loader.loadModel(self.path + '/frontwheel')
            self.rear_right_wheel_np = eng.loader.loadModel(self.path + '/rearwheel')
            self.rear_left_wheel_np = eng.loader.loadModel(self.path + '/rearwheel')
        except IOError:
            self.front_right_wheel_np = eng.loader.loadModel(self.path + '/wheel')
            self.front_left_wheel_np = eng.loader.loadModel(self.path + '/wheel')
            self.rear_right_wheel_np = eng.loader.loadModel(self.path + '/wheel')
            self.rear_left_wheel_np = eng.loader.loadModel(self.path + '/wheel')
        taskMgr.doMethodLater(.01, self.cb, 'callback')

    def destroy(self):
        '''The destroyer.'''
        meshes = [self.nodepath,
                  self.chassis_np,
                  self.front_right_wheel_np,
                  self.front_left_wheel_np,
                  self.rear_right_wheel_np,
                  self.rear_right_wheel_np]
        map(lambda mesh: mesh.removeNode(), meshes)
