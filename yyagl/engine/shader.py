from panda3d.core import AmbientLight, DirectionalLight, PointLight, \
    Spotlight, LVector4f, LVector3f, Vec3, Shader, Texture, WindowProperties,\
    FrameBufferProperties, GraphicsPipe, GraphicsOutput, NodePath, PandaNode
from direct.filter.FilterManager import FilterManager
from ..gameobject import Colleague


class ShaderMgr(Colleague):

    def __init__(self, mdt):
        Colleague.__init__(self, mdt)
        self.lights = []
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
        gamma_val = game.options['development']['gamma']
        final_quad.set_shader_input('gamma', gamma_val)
        final_quad.setShaderInput('input_tex', final_tex)

    def apply(self):
        winprops = WindowProperties.size(2048, 2048)
        props = FrameBufferProperties()
        props.setRgbColor(1)
        props.setAlphaBits(1)
        props.setDepthBits(1)
        lbuffer = base.graphicsEngine.makeOutput(
            base.pipe, 'offscreen buffer', -2, props, winprops,
            GraphicsPipe.BFRefuseWindow, base.win.getGsg(), base.win)
        self.buffer = lbuffer
        ldepthmap = Texture()
        lbuffer.addRenderTexture(ldepthmap, GraphicsOutput.RTMBindOrCopy,
                                 GraphicsOutput.RTPDepthStencil)
        ldepthmap.setMinfilter(Texture.FTShadow)
        ldepthmap.setMagfilter(Texture.FTShadow)

        base.camLens.setNearFar(1.0, 10000)
        base.camLens.setFov(75)

        self.lcam = base.makeCamera(lbuffer)
        self.lcam.node().setScene(render)
        self.lcam.node().getLens().setFov(45)
        self.lcam.node().getLens().setNearFar(1, 100)

        render.setShaderInput('light', self.lcam)
        render.setShaderInput('depthmap', ldepthmap)
        render.setShaderInput('ambient', .15, .15, .15, 1.0)

        lci = NodePath(PandaNode('light camera initializer'))
        with open('racing/game/assets/shaders/caster.vert') as f: vert = f.read()
        with open('racing/game/assets/shaders/caster.frag') as f: frag = f.read()
        lci.setShader(Shader.make(Shader.SLGLSL, vert, frag))
        self.lcam.node().setInitialState(lci.getState())

        mci = NodePath(PandaNode('main camera initializer'))
        with open('racing/game/assets/shaders/main.vert') as f: vert = f.read()
        with open('racing/game/assets/shaders/main.frag') as f: frag = f.read()
        frag = frag.replace('<LIGHTS>', str(len(self.lights)))
        render.setShader(Shader.make(Shader.SLGLSL, vert, frag))
        render.setShaderInput('num_lights', len(self.lights))
        map(lambda lgt: self.set_lgt_args(*lgt), enumerate(self.lights))
        mci.setShader(Shader.make(Shader.SLGLSL, vert, frag))
        base.cam.node().setInitialState(mci.getState())

        self.lcam.setPos(15, 30, 45)
        self.lcam.lookAt(0, 15, 0)
        self.lcam.node().getLens().setNearFar(1, 100)

    def toggle_shader(self):
        if render.getShader():
            render.set_shader_off()
            render.setShaderAuto()
            return
        self.apply()
