from os.path import exists
from racing.game.gameobject import Gfx
from panda3d.bullet import BulletRigidBodyNode, BulletBoxShape, BulletSphereShape
from panda3d.core import Mat4


class RocketGfx(Gfx):

    def __init__(self, mdt):
        self.gfx_np = None
        Gfx.__init__(self, mdt)

    def sync_build(self):
        self.gfx_np = loader.loadModel('assets/models/weapons/rocket/rocket')
        self.gfx_np.flattenLight()
        self.gfx_np.reparentTo(self.mdt.car.gfx.nodepath)
        self.gfx_np.set_h(180)
        self.gfx_np.set_scale(1.5)
        self.gfx_np.setPos(0, 0, 1.5)

    def destroy(self):
        self.gfx_np.remove_node()
        self.gfx_np = None
        Gfx.destroy(self)
