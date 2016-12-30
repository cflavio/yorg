from os.path import exists
from racing.game.gameobject import Logic
from panda3d.bullet import BulletRigidBodyNode, BulletBoxShape, BulletSphereShape
from panda3d.core import Mat4


class RocketLogic(Logic):

    def fire(self):
        self.mdt.phys.fire()
        self.mdt.audio.sfx.play()
        taskMgr.doMethodLater(5, lambda tsk: self.mdt.destroy(), 'destroy rocket')

    def destroy(self):
        self.mdt.car.logic.weapon = None
        Logic.destroy(self)
