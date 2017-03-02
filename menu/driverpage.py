from direct.gui.DirectGuiGlobals import DISABLED, NORMAL
from yyagl.engine.gui.page import Page, PageGui
from yyagl.engine.gui.imgbtn import ImageButton
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import TextureStage, Shader, Texture, PNMImage, TextNode
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectEntry import DirectEntry
from random import shuffle


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
        menu_args = self.menu.gui.menu_args

        txt = OnscreenText(text=_('Select the driver'), pos=(0, .8),
                           **menu_gui.text_args)
        self.widgets += [txt]

        self.track_path = 'tracks/' + self.menu.track
        t_a = self.menu.gui.text_args.copy()
        del t_a['scale']
        names = open('assets/thanks.txt').readlines()
        shuffle(names)
        names = names[:9]
        name = OnscreenText(_('Write your name:'), pos=(-.1, .6), scale=.06,
                            align=TextNode.A_right, **t_a)
        self.ent = DirectEntry(
            scale=.08, pos=(0, 1, .6), entryFont=menu_args.font, width=12,
            frameColor=menu_args.btn_color,
            initialText=_('your name'))
        self.ent.onscreenText['fg'] = (.75, .75, .25, 1)
        self.widgets += [name, self.ent]
        self.drivers = []
        for row in range(2):
            for col in range(4):
                idx = (col + 1) + row * 4
                img = ImageButton(
                    scale=.24, pos=(-.75 + col * .5, 1, .25 - row * .5),
                    frameColor=(0, 0, 0, 0),
                    image='assets/images/drivers/driver%s.png' % idx,
                    command=self.on_click, extraArgs=[idx],
                    **self.menu.gui.imgbtn_args)
                thanks = OnscreenText(
                    _('thanks to:'), pos=(-.75 + col * .5, .1 - row * .5),
                    scale=.038, **t_a)
                name = OnscreenText(
                    names[idx - 1], pos=(-.75 + col * .5, .04 - row * .5),
                    scale=.045, **t_a)
                self.widgets += [img, thanks, name]
                self.drivers += [img]
        self.img = OnscreenImage(
            'assets/images/cars/%s_sel.png' % self.mdt.car,
            parent=base.a2dBottomRight, pos=(-.38, 1, .38), scale=.32)
        self.widgets += [self.img]
        shader = Shader.make(Shader.SL_GLSL, vert, frag)
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
        self.update_tsk = taskMgr.add(self.update_text, 'update text')
        for drv in self.drivers:
            drv['state'] = DISABLED
            drv.setShaderInput('enable', .2)

    def update_text(self, task):
        has_name = self.ent.get() != _('your name')
        if has_name and self.ent.get().startswith(_('your name')):
            self.ent.enterText(self.ent.get()[len(_('your name')):])
            for drv in self.drivers:
                drv['state'] = NORMAL
                drv.setShaderInput('enable', 1)
        elif self.ent.get() in [_('your name')[:-1], '']:
            self.ent.enterText('')
            for drv in self.drivers:
                drv['state'] = DISABLED
                drv.setShaderInput('enable', .2)
        elif self.ent.get() not in [_('your name'), '']:
            for drv in self.drivers:
                drv['state'] = NORMAL
                drv.setShaderInput('enable', 1)
        return task.cont

    def on_click(self, i):
        txt_path = 'assets/images/drivers/driver%s_sel.png'
        self.img.setTexture(self.ts, loader.loadTexture(txt_path % i))
        self.widgets[-1]['state'] = DISABLED
        for drv in self.drivers:
            drv['state'] = DISABLED
            drv.setShaderInput('enable', .2)
        taskMgr.remove(self.update_tsk)
        names = open('assets/thanks.txt').readlines()
        shuffle(names)
        names = names[:5]
        cars = ['kronos', 'themis', 'diones', 'iapeto']
        cars.remove(self.mdt.car)
        shuffle(cars)
        drv_idx = range(1, 9)
        drv_idx.remove(i)
        shuffle(drv_idx)
        drivers = [(i, self.ent.get(), self.mdt.car)]
        drivers += [(drv_idx[j], names[j], cars[j]) for j in range(3)]
        game.logic.season.logic.drivers = drivers
        args = ('Race', self.mdt.track, self.mdt.car, [], drivers)
        taskMgr.doMethodLater(2.0, lambda tsk: game.fsm.demand(*args), 'start')

    def destroy(self):
        PageGui.destroy(self)
        self.img = None
        taskMgr.remove(self.update_tsk)


class DriverPage(Page):
    gui_cls = DriverPageGui

    def __init__(self, menu, track, car):
        self.track = track
        self.car = car
        Page.__init__(self, menu)
