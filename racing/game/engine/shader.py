from panda3d.core import AmbientLight, DirectionalLight, PointLight, \
    Spotlight, LVector4f, LVector3f, Vec3, Shader, Texture
from direct.filter.FilterManager import FilterManager
from ..gameobject import Colleague


class ShaderMgr(Colleague):

    def __init__(self, mdt):
        Colleague.__init__(self, mdt)
        self.lights = []
        with open('racing/game/assets/shaders/main.vert') as f:
            self.vert = f.read()
        with open('racing/game/assets/shaders/main.frag') as f:
            self.frag = f.read()
        if game.options['development']['shaders']:
            self.setup_post_fx()

    def set_lgt(self, lgt):
        lnp = render.attachNewNode(lgt)
        self.lights += [lnp]
        render.set_light(lnp)

    def set_amb_lgt(self, col):
        lgt = AmbientLight('ambient light')
        lgt.setColor(col)
        self.set_lgt(lgt)

    def set_dir_lgt(self, col, direction):
        lgt = DirectionalLight('directional light')
        lgt.setColor(col)
        self.set_lgt(lgt)
        self.lights[-1].setHpr(*direction)

    def set_pnt_lgt(self, col, pos):
        lgt = PointLight('point light')
        lgt.setColor(col)
        self.set_lgt(lgt)
        self.lights[-1].setPos(*pos)

    def set_spotlight(self, col, exp, cutoff, pos, look_at):
        lgt = Spotlight('spotlight')
        lgt.setColor(col)
        lgt.setExponent(exp)
        lgt.getLens().setFov(cutoff, cutoff)
        self.set_lgt(lgt)
        self.lights[-1].setPos(*pos)
        self.lights[-1].lookAt(*look_at)

    def set_default_args(self, idx):
        pref = 'lights[%s].' % idx
        render.setShaderInput(pref + 'pos', LVector4f(0, 0, 0, 1))
        render.setShaderInput(pref + 'amb', LVector3f(0, 0, 0))
        render.setShaderInput(pref + 'diff', LVector3f(0, 0, 0))
        render.setShaderInput(pref + 'spec', LVector3f(0, 0, 0))
        render.setShaderInput(pref + 'dir', LVector3f(0, 0, 0))
        render.setShaderInput(pref + 'exp', .0)
        render.setShaderInput(pref + 'cutoff', .0)

    def set_lgt_args(self, idx, lgt):
        self.set_default_args(idx)
        pref = 'lights[%s].' % idx
        if lgt.node().__class__ == AmbientLight:
            render.setShaderInput(pref + 'amb', lgt.node().get_color())
        elif lgt.node().__class__ == PointLight:
            lgt_pos = lgt.get_mat(base.cam).xform(LVector4f(0, 0, 0, 1))
            render.setShaderInput(pref + 'pos', lgt_pos)
            render.setShaderInput(pref + 'diff', lgt.node().get_color())
            render.setShaderInput(pref + 'spec', lgt.node().get_color())
        elif lgt.node().__class__ == DirectionalLight:
            lgt_pos = lgt.get_pos()
            lgt_vec = -render.getRelativeVector(lgt, Vec3(0, 1, 0))
            lgt_pos = LVector4f(lgt_vec[0], lgt_vec[1], lgt_vec[2], 0)
            render.setShaderInput(pref + 'pos', lgt_pos)
            render.setShaderInput(pref + 'diff', lgt.node().get_color())
            render.setShaderInput(pref + 'spec', lgt.node().get_color())
        elif lgt.node().__class__ == Spotlight:
            lgt_pos = lgt.get_mat(base.cam).xform(LVector4f(0, 0, 0, 1))
            lgt_vec =  base.cam.getRelativeVector(lgt, Vec3(0, 1, 0))
            render.setShaderInput(pref + 'pos', lgt_pos)
            render.setShaderInput(pref + 'diff', lgt.node().get_color())
            render.setShaderInput(pref + 'spec', lgt.node().get_color())
            render.setShaderInput(pref + 'dir', lgt_vec)
            render.setShaderInput(pref + 'exp', lgt.node().get_exponent())
            render.setShaderInput(pref + 'cutoff', lgt.node().getLens().getFov()[0])

    def clear_lights(self):
        for light in self.lights:
            eng.base.render.clearLight(light)
            light.removeNode()
        self.lights = []

    def setup_post_fx(self):
        self.filter_mgr = FilterManager(base.win, base.cam)
        col_tex = Texture()
        final_tex = Texture()
        final_quad = self.filter_mgr.renderSceneInto(colortex=col_tex)
        inter_quad = self.filter_mgr.renderQuadInto(colortex=final_tex)
        with open('racing/game/assets/shaders/filter.vert') as f:
            vert = f.read()
        with open('racing/game/assets/shaders/filter.frag') as f:
            frag = f.read()
        inter_quad.setShader(Shader.make(Shader.SLGLSL, vert, frag))
        inter_quad.setShaderInput('input_tex', col_tex)
        with open('racing/game/assets/shaders/pass.frag') as f:
            frag = f.read()
        final_quad.setShader(Shader.make(Shader.SLGLSL, vert, frag))
        final_quad.setShaderInput('input_tex', final_tex)

    def toggle_shader(self):
        if render.getShader():
            render.set_shader_off()
            render.setShaderAuto()
            return
        frag = self.frag.replace('<LIGHTS>', str(len(self.lights)))
        render.setShader(Shader.make(Shader.SLGLSL, self.vert, frag))
        render.setShaderInput('num_lights', len(self.lights))
        map(lambda lgt: self.set_lgt_args(*lgt), enumerate(self.lights))
