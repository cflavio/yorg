from os.path import exists
from yyagl.gameobject import Phys
from panda3d.bullet import BulletRigidBodyNode, BulletBoxShape, \
    BulletSphereShape, BulletGhostNode
from panda3d.core import Mat4


class BonusPhys(Phys):

    def __init__(self, mdt, pos):
        self.pos = pos
        eng.phys.attach(mdt.event.on_collision)
        Phys.__init__(self, mdt)

    def sync_build(self):
        self.ghost = BulletGhostNode('Bonus')
        self.ghost.addShape(BulletBoxShape((1, 1, 2.5)))
        ghostNP = render.attachNewNode(self.ghost)
        ghostNP.setPos(self.pos)
        eng.phys.world_phys.attachGhost(self.ghost)

    def destroy(self):
        eng.phys.detach(self.mdt.event.on_collision)
        eng.phys.world_phys.removeGhost(self.ghost)
        self.ghost = None
        Phys.destroy(self)