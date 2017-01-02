from os.path import exists
from yyagl.gameobject import Audio
from panda3d.bullet import BulletRigidBodyNode, BulletBoxShape, BulletSphereShape
from panda3d.core import Mat4


class RocketAudio(Audio):

    def __init__(self, mdt):
        Audio.__init__(self, mdt)
        self.sfx = loader.loadSfx('assets/sfx/landing.ogg')
