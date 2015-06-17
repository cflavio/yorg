from ya2.gameobject import Gfx
from panda3d.bullet import BulletRigidBodyNode


class _Gfx(Gfx):
    '''This class models the graphics component of a car.'''

    def __init__(self, mdt):
        Gfx.__init__(self, mdt)
        vehicle_node = BulletRigidBodyNode('Vehicle')
        self.nodepath = eng.world_np.attachNewNode(vehicle_node)

        self.chassis_np = eng.loader.loadModel('car/car')
        self.chassis_np.reparentTo(self.nodepath)
        self.chassis_np.setDepthOffset(-2)

        self.front_right_wheel_np = eng.loader.loadModel('car/frontwheel')
        self.front_right_wheel_np.reparentTo(eng.world_np)

        self.front_left_wheel_np = eng.loader.loadModel('car/frontwheel')
        self.front_left_wheel_np.reparentTo(eng.world_np)

        self.rear_right_wheel_np = eng.loader.loadModel('car/rearwheel')
        self.rear_right_wheel_np.reparentTo(eng.world_np)

        self.rear_left_wheel_np = eng.loader.loadModel('car/rearwheel')
        self.rear_left_wheel_np.reparentTo(eng.world_np)

    def destroy(self):
        '''The destroyer.'''
        meshes = [self.nodepath,
                  self.chassis_np,
                  self.front_right_wheel_np,
                  self.front_left_wheel_np,
                  self.rear_right_wheel_np,
                  self.rear_right_wheel_np]
        map(lambda mesh: mesh.removeNode(), meshes)
