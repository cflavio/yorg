from panda3d.core import getModelPath, LightRampAttrib, PandaNode, NodePath, \
    AntialiasAttrib
from direct.particles.ParticleEffect import ParticleEffect
from direct.filter.CommonFilters import CommonFilters
from ..gameobject.gameobject import Gfx
import os


class EngineGfx(Gfx):

    def __init__(self, mdt):
        Gfx.__init__(self, mdt)
        getModelPath().appendDirectory(eng.logic.conf.model_path)
        mdt.base.enableParticles()
        render.setShaderAuto()
        render.setTwoSided(True)
        if eng.logic.conf.antialiasing:
            render.setAntialias(AntialiasAttrib.MAuto)
        self.world_np = None

    def init(self):
        self.world_np = render.attachNewNode('world')

    def clean(self):
        self.world_np.removeNode()

    @staticmethod
    def load_model(*args, **kwargs):
        if os.path.exists(args[0] + '.bam'):
            args[0] += '.bam'
        loader.loadModel(*args, **kwargs)

    @staticmethod
    def __set_toon():
        tempnode = NodePath(PandaNode('temp node'))
        tempnode.setAttrib(LightRampAttrib.makeSingleThreshold(.5, .4))
        tempnode.setShaderAuto()
        base.cam.node().setInitialState(tempnode.getState())
        CommonFilters(base.win, base.cam).setCartoonInk(separation=1)

    def print_stats(self):
        print '\n\n#####\nrender2d.analyze()'
        self.render2d.analyze()
        print '\n\n#####\nrender.analyze()'
        self.render.analyze()
        print '\n\n#####\nrender2d.ls()'
        self.render2d.ls()
        print '\n\n#####\nrender.ls()'
        self.render.ls()

    @staticmethod
    def particle(path, parent, render_parent, pos, timeout):
        par = ParticleEffect()
        par.loadConfig(path)
        par.start(parent=parent, renderParent=render_parent)
        par.setPos(pos)
        args = (timeout, lambda par: par.cleanup(), 'clear', [par])
        taskMgr.doMethodLater(*args)
