from os.path import exists
from racing.game.gameobject import Event
from panda3d.bullet import BulletRigidBodyNode, BulletBoxShape, BulletSphereShape,\
    BulletGhostNode
from panda3d.core import Mat4


class BonusEvent(Event):

    def on_collision(self, obj, obj_name):
        if obj_name == 'Bonus' and obj in self.mdt.phys.ghost.getOverlappingNodes():
            game.track.phys.bonuses.remove(self.mdt)
            self.mdt.destroy()
