from collections import namedtuple
from itertools import product
from random import shuffle
from panda3d.core import TextureStage, Shader, Texture, PNMImage, TextNode
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectEntry import DirectEntry
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.DirectGuiGlobals import DISABLED, NORMAL
from yyagl.engine.gui.page import Page, PageGui, PageFacade
from yyagl.engine.gui.imgbtn import ImgBtn
from yyagl.gameobject import GameObject
from yorg.thanksnames import ThanksNames
from .thankspage import ThanksPageGui


frag = '''#version 120
varying vec2 texcoord;
uniform sampler2D p3d_Texture0;
uniform sampler2D p3d_Texture1;

void main() {
    float dist_l = texcoord.x;
    float dist_r = 1 - texcoord.x;
    float dist_u = texcoord.y;
    float dist_b = 1 - texcoord.y;
    float alpha = min(dist_l, min(dist_r, min(dist_u, dist_b))) * 30;
    vec4 pix_a = texture2D(p3d_Texture0, texcoord);
    vec4 pix_b = texture2D(p3d_Texture1, texcoord);
    vec4 tex_col = mix(pix_a, pix_b, pix_b.a);
    gl_FragColor = tex_col * vec4(1, 1, 1, alpha);
}'''


class DriverPageGui(ThanksPageGui):

    def __init__(self, mdt, driverpage_props):
        self.props = driverpage_props
        self.sel_drv_img = None
        ThanksPageGui.__init__(self, mdt, driverpage_props.gameprops.menu_args)

    def bld_page(self):
        self.drv_info = self.props.gameprops.drivers_info
        menu_args = self.menu_args
        widgets = [OnscreenText(text=_('Select the driver'), pos=(0, .8),
                                **menu_args.text_args)]
        t_a = self.menu_args.text_args.copy()
        del t_a['scale']
        name = OnscreenText(_('Write your name:'), pos=(-.1, .6), scale=.06,
                            align=TextNode.A_right, **t_a)
        self.ent = DirectEntry(
            scale=.08, pos=(0, 1, .6), entryFont=menu_args.font, width=12,
            frameColor=menu_args.btn_color,
            initialText=self.props.gameprops.player_name or _('your name'))
        self.ent.onscreenText['fg'] = menu_args.text_fg
        self.drivers = []
        for row, col in product(range(2), range(4)):
            idx = (col + 1) + row * 4
            drv_btn = ImgBtn(
                scale=.24, pos=(-.75 + col * .5, 1, .25 - row * .5),
                frameColor=(0, 0, 0, 0), image=self.props.gameprops.drivers_img[0] % idx,
                command=self.on_click, extraArgs=[idx],
                **self.menu_args.imgbtn_args)
            widgets += [drv_btn]
            self.drivers += [widgets[-1]]
            sign = lambda pos_x: '\1green\1+\2' if pos_x > 0 else ''
            psign = lambda pos_x, sgn=sign: '+' if pos_x == 0 else sgn(pos_x)

            def ppcol(x):
                return '\1green\1%s\2' % x if x > 0 else '\1red\1%s\2' % x
            pcol = lambda x: x if x == 0 else ppcol(x)
            lab_lst = [(_('adherence'), .04), (_('speed'), .16),
                       (_('stability'), .1)]
            widgets += map(lambda lab_def: self.__add_lab(*(lab_def + (row, col))), lab_lst)
            txt_lst = [(self.drv_info[idx - 1].adherence, .04),
                       (self.drv_info[idx - 1].speed, .16),
                       (self.drv_info[idx - 1].stability, .1)]
            widgets += map(lambda txt_def: self.__add_txt(*txt_def + (psign, pcol, col, row)), txt_lst)
        self.sel_drv_img = OnscreenImage(
            self.props.gameprops.cars_img % self.mdt.car, parent=base.a2dBottomRight,
            pos=(-.38, 1, .38), scale=.32)
        widgets += [self.sel_drv_img, name, self.ent]
        map(self.add_widget, widgets)
        ffilterpath = self.eng.curr_path + 'yyagl/assets/shaders/filter.vert'
        with open(ffilterpath) as ffilter:
            vert = ffilter.read()
        shader = Shader.make(Shader.SL_GLSL, vert, frag)
        self.sel_drv_img.set_shader(shader)
        self.sel_drv_img.set_transparency(True)
        self.t_s = TextureStage('ts')
        self.t_s.set_mode(TextureStage.MDecal)
        empty_img = PNMImage(1, 1)
        empty_img.add_alpha()
        empty_img.alpha_fill(0)
        tex = Texture()
        tex.load(empty_img)
        self.sel_drv_img.set_texture(self.t_s, tex)
        ThanksPageGui.bld_page(self)
        self.update_tsk = taskMgr.add(self.update_text, 'update text')
        self.enable_buttons(False)

    def __add_lab(self, txt, pos_z, row, col):
        t_a = self.menu_args.text_args.copy()
        del t_a['scale']
        return OnscreenText(
            txt + ':', pos=(-.95 + col * .5, pos_z - row * .5),
            scale=.046, align=TextNode.A_left, **t_a)

    def __add_txt(self, val, pos_z, psign, pcol, col, row):
        t_a = self.menu_args.text_args.copy()
        del t_a['scale']
        return OnscreenText(
            '%s%s%%' % (psign(val), pcol(val)),
            pos=(-.55 + col * .5, pos_z - row * .5), scale=.052,
            align=TextNode.A_right, **t_a)

    def enable_buttons(self, enable):
        [(drv.enable if enable else drv.disable)() for drv in self.drivers]

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
        return task.cont  # don't do a task, attach to modifications events

    def on_click(self, i):
        txt_path = self.props.gameprops.drivers_img.path_sel
        self.sel_drv_img.setTexture(self.t_s, loader.loadTexture(txt_path % i))
        self.widgets[-1]['state'] = DISABLED
        self.enable_buttons(False)
        taskMgr.remove(self.update_tsk)
        names = ThanksNames.get_thanks(7, 5)
        cars = self.props.gameprops.cars_names[:]
        cars.remove(self.mdt.car)
        shuffle(cars)
        drv_idx = range(1, 9)
        drv_idx.remove(i)
        shuffle(drv_idx)
        #drivers = [DriverInfo(i, self.ent.get(), self.drv_info[i - 1], self.mdt.car)]
        #drivers += [DriverInfo(drv_idx[j], names[j], self.drv_info[j - 1], cars[j])
        #            for j in range(len(cars))]
        self.props.gameprops.drivers_info[i] = self.props.gameprops.drivers_info[i]._replace(img_idx=i)
        self.props.gameprops.drivers_info[i] = self.props.gameprops.drivers_info[i]._replace(name=self.ent.get())
        self.notify('on_driver_selected', self.ent.get(), self.mdt.track, self.mdt.car)

    def destroy(self):
        self.sel_drv_img = None
        taskMgr.remove(self.update_tsk)
        PageGui.destroy(self)


class DriverPage(Page):
    gui_cls = DriverPageGui

    def __init__(self, track, car, driverpage_props):
        self.track = track
        self.car = car
        init_lst = [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [self, driverpage_props])]]
        GameObject.__init__(self, init_lst)
        PageFacade.__init__(self)
