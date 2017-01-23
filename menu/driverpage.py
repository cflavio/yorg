from direct.gui.DirectButton import DirectButton
from direct.gui.DirectGuiGlobals import DISABLED, NORMAL
from yyagl.engine.gui.page import Page, PageGui
from yyagl.racing.season.season import SingleRaceSeason
from yyagl.engine.gui.imgbtn import ImageButton
from .netmsgs import NetMsgs
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import TextureStage, Shader, Texture, PNMImage
from direct.gui.OnscreenText import OnscreenText


vert = '''#version 130
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;
uniform mat4 p3d_ModelViewProjectionMatrix;
out vec2 texcoord;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    texcoord = p3d_MultiTexCoord0;
}'''


frag = '''#version 130
in vec2 texcoord;
uniform sampler2D p3d_Texture0;
uniform sampler2D p3d_Texture1;
out vec4 p3d_FragColor;

void main() {
    float dist_l = texcoord.x;
    float dist_r = 1 - texcoord.x;
    float dist_u = texcoord.y;
    float dist_b = 1 - texcoord.y;
    float alpha = min(dist_l, min(dist_r, min(dist_u, dist_b))) * 30;
    vec4 pix_a = texture(p3d_Texture0, texcoord);
    vec4 pix_b = texture(p3d_Texture1, texcoord);
    vec4 tex_col = mix(pix_a, pix_b, pix_b.a);
    p3d_FragColor = tex_col * vec4(1, 1, 1, alpha);
}'''


class DriverPageGui(PageGui):

    def __init__(self, mdt, menu):
        PageGui.__init__(self, mdt, menu)

    def build_page(self):
        menu_gui = self.menu.gui

        txt = OnscreenText(text=_('Select the driver'), pos=(0, .8), **menu_gui.text_args)
        self.widgets += [txt]

        self.track_path = 'tracks/' + self.menu.track
        self.widgets += [
            ImageButton(
                scale=.4, pos=(-1.6 + i * .8, 1, .3), frameColor=(0, 0, 0, 0),
                image='assets/images/drivers/driver%s.png' % i,
                command=self.on_click, extraArgs=[i],
                **self.menu.gui.imgbtn_args)
            for i in range(1, 4)]
        self.img = OnscreenImage(
                'assets/images/cars/%s_sel.png' % self.mdt.car,
                parent=base.a2dBottomRight, pos=(-.5, 1, .5), scale=.4)
        self.widgets += [self.img]
        shader = Shader.make(Shader.SL_GLSL, vertex=vert, fragment=frag)
        self.img.setShader(shader)
        self.img.setTransparency(True)
        self.ts = TextureStage('ts')
        self.ts.setMode(TextureStage.MDecal)
        empty_img = PNMImage(1, 1)
        empty_img.add_alpha()
        empty_img.alpha_fill(0)
        tex = Texture()
        tex.load(empty_img)
        self.img.setTexture(self.ts, tex)
        PageGui.build_page(self)

    def on_click(self, i):
        self.img.setTexture(self.ts, loader.loadTexture('assets/images/drivers/driver%s_sel.png' % i))
        self.widgets[-1]['state'] = DISABLED
        taskMgr.doMethodLater(2.0, lambda tsk: game.fsm.demand('Race', self.mdt.track, self.mdt.car, [], str(i)), 'start')

    def destroy(self):
        PageGui.destroy(self)
        self.img = None


class DriverPage(Page):
    gui_cls = DriverPageGui

    def __init__(self, menu, track, car):
        self.track = track
        self.car = car
        Page.__init__(self, menu)
