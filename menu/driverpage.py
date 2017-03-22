from random import shuffle
from panda3d.core import TextureStage, Shader, Texture, PNMImage, TextNode,\
    TextPropertiesManager, TextProperties
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectEntry import DirectEntry
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.DirectGuiGlobals import DISABLED, NORMAL
from yyagl.engine.gui.page import Page, PageGui
from yyagl.engine.gui.imgbtn import ImageButton
from yyagl.gameobject import GameObjectMdt
from yorg.utils import Utils


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

    def __init__(self, mdt, menu, player_name, drivers_img, cars_img, cars):
        self.player_name = player_name
        self.drivers_img = drivers_img
        self.cars_img = cars_img
        self.cars = cars
        PageGui.__init__(self, mdt, menu)

    def build_page(self):
        self.skills = [drv[2] for drv in game.logic.drivers]
        menu_gui = self.menu.gui
        menu_args = self.menu.gui.menu_args

        txt = OnscreenText(text=_('Select the driver'), pos=(0, .8),
                           **menu_gui.text_args)
        widgets = [txt]

        self.track_path = self.menu.track
        t_a = self.menu.gui.text_args.copy()
        del t_a['scale']
        names = Utils().get_thanks(8)
        name = OnscreenText(_('Write your name:'), pos=(-.1, .6), scale=.06,
                            align=TextNode.A_right, **t_a)
        player_name = self.player_name
        self.ent = DirectEntry(
            scale=.08, pos=(0, 1, .6), entryFont=menu_args.font, width=12,
            frameColor=menu_args.btn_color,
            initialText=player_name or _('your name'))
        self.ent.onscreenText['fg'] = menu_args.text_fg
        widgets += [name, self.ent]
        self.drivers = []
        for row in range(2):
            for col in range(4):
                idx = (col + 1) + row * 4
                img = ImageButton(
                    scale=.24, pos=(-.75 + col * .5, 1, .25 - row * .5),
                    frameColor=(0, 0, 0, 0),
                    image=self.drivers_img[0] % idx,
                    command=self.on_click, extraArgs=[idx],
                    **self.menu.gui.imgbtn_args)
                thanks = OnscreenText(
                    _('thanks to:'), pos=(-.75 + col * .5, .1 - row * .5),
                    scale=.038, **t_a)
                name = OnscreenText(
                    names[idx - 1], pos=(-.75 + col * .5, .04 - row * .5),
                    scale=.045, **t_a)
                tp_mgr = TextPropertiesManager.getGlobalPtr()
                colors = [(.75, .25, .25, 1), (.25, .75, .25, 1)]
                for namecol, tpcol in zip(['red', 'green'], colors):
                    _tp = TextProperties()
                    _tp.setTextColor(tpcol)
                    tp_mgr.setProperties(namecol, _tp)
                sign = lambda x: '\1green\1+\2' if x > 0 else ''
                psign = lambda x: '+' if x == 0 else sign(x)
                def ppcol(x):
                    return '\1green\1%s\2' % x if x > 0 else '\1red\1%s\2' % x
                pcol = lambda x: x if x == 0 else ppcol(x)
                fric_lab = OnscreenText(
                    _('adherence') + ':', pos=(-.95 + col * .5, .4 - row * .5),
                    scale=.046, align=TextNode.A_left, **t_a)
                speed_lab = OnscreenText(
                    _('speed') + ':', pos=(-.95 + col * .5, .3 - row * .5),
                    scale=.046, align=TextNode.A_left, **t_a)
                roll_lab = OnscreenText(
                    _('stability') + ':', pos=(-.95 + col * .5, .2 - row * .5),
                    scale=.046, align=TextNode.A_left, **t_a)
                fric_txt = OnscreenText(
                    '%s%s%%' % (psign(self.skills[idx - 1][1]),
                                pcol(self.skills[idx - 1][1])),
                    pos=(-.55 + col * .5, .4 - row * .5), scale=.052,
                    align=TextNode.A_right, **t_a)
                speed_txt = OnscreenText(
                    '%s%s%%' % (psign(self.skills[idx - 1][0]),
                                pcol(self.skills[idx - 1][0])),
                    pos=(-.55 + col * .5, .3 - row * .5), scale=.052,
                    align=TextNode.A_right, **t_a)
                roll_txt = OnscreenText(
                    '%s%s%%' % (psign(self.skills[idx - 1][2]),
                                pcol(self.skills[idx - 1][2])),
                    pos=(-.55 + col * .5, .2 - row * .5), scale=.052,
                    align=TextNode.A_right, **t_a)
                widgets += [
                    img, thanks, name, speed_lab, fric_lab, roll_lab,
                    speed_txt, fric_txt, roll_txt]
                self.drivers += [img]
        self.img = OnscreenImage(
            self.cars_img % self.mdt.car,
            parent=base.a2dBottomRight, pos=(-.38, 1, .38), scale=.32)
        widgets += [self.img]
        map(self.add_widget, widgets)
        with open('yyagl/assets/shaders/filter.vert') as ffilter:
            vert = ffilter.read()
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
        self.enable_buttons(False)

    def enable_buttons(self, enable):
        for drv in self.drivers:
            drv['state'] = NORMAL if enable else DISABLED
            drv.setShaderInput('enable', 1 if enable else .2)

    def update_text(self, task):
        has_name = self.ent.get() != _('your name')
        if has_name and self.ent.get().startswith(_('your name')):
            self.ent.enterText(self.ent.get()[len(_('your name')):])
            self.enable_buttons(True)
        elif self.ent.get() in [_('your name')[:-1], '']:
            self.ent.enterText('')
            self.enable_buttons(False)
        elif self.ent.get() not in [_('your name'), '']:
            self.enable_buttons(True)
        return task.cont

    def on_click(self, i):
        txt_path = self.drivers_img[1]
        self.img.setTexture(self.ts, loader.loadTexture(txt_path % i))
        self.widgets[-1]['state'] = DISABLED
        self.enable_buttons(False)
        taskMgr.remove(self.update_tsk)
        names = Utils().get_thanks(4)
        cars = self.cars[:]
        cars.remove(self.mdt.car)
        shuffle(cars)
        drv_idx = range(1, 9)
        drv_idx.remove(i)
        shuffle(drv_idx)
        drivers = [(i, self.ent.get(), self.skills[i], self.mdt.car)]
        drivers += [(drv_idx[j], names[j], self.skills[j], cars[j]) for j in range(3)]
        self.mdt.menu.gui.notify('on_driver_selected', self.ent.get(), drivers,
                                 self.mdt.track, self.mdt.car)

    def destroy(self):
        self.img = None
        taskMgr.remove(self.update_tsk)
        PageGui.destroy(self)


class DriverPage(Page):
    gui_cls = DriverPageGui

    def __init__(self, menu, track, car, player_name, drivers_img, cars_img,
                 cars):
        self.track = track
        self.car = car
        self.menu = menu
        init_lst = [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [self, self.menu, player_name, drivers_img,
                                    cars_img, cars])]]
        GameObjectMdt.__init__(self, init_lst)
