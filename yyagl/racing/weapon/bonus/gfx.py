from os.path import exists
from yyagl.gameobject import Gfx
from panda3d.bullet import BulletRigidBodyNode, BulletBoxShape, \
    BulletSphereShape, BulletGhostNode
from panda3d.core import Mat4


class BonusGfx(Gfx):

    def __init__(self, mdt, pos):
        self.model = None
        self.pos = pos
        Gfx.__init__(self, mdt)

    def sync_build(self):
        self.model = loader.loadModel('assets/models/weapons/bonus/bonus')
        self.model.reparent_to(render)
        self.model.set_pos(self.pos)

    def destroy(self):
        self.model.remove_node()
        self.model = None
        Gfx.destroy(self)