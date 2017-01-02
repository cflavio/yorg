from os.path import exists
from yyagl.gameobject import Phys
from panda3d.bullet import BulletRigidBodyNode, BulletBoxShape, BulletSphereShape
from panda3d.core import Mat4


class RocketPhys(Phys):

    def fire(self):
        self.node = BulletRigidBodyNode('Box')
        self.node.setMass(10000)
        self.node.addShape(BulletSphereShape(.5))
        self.np = self.mdt.car.gfx.nodepath.attachNewNode(self.node)
        self.np.setPos(0, 0, 1.5)
        eng.phys.world_phys.attachRigidBody(self.node)
        self.mdt.gfx.gfx_np.reparentTo(self.np)
        self.mdt.gfx.gfx_np.setPos(0, 0, 0)
        rot_mat = Mat4()
        rot_mat.setRotateMat(self.mdt.car.gfx.nodepath.get_h(), (0, 0, 1))
        self.node.setLinearVelocity(rot_mat.xformVec((0, 30, 0)))

    def destroy(self):
        if hasattr(self, 'node'):  # has not been fired
            eng.phys.world_phys.removeRigidBody(self.node)
            self.np.remove_node()
            self.np = None
        Phys.destroy(self)
