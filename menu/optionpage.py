from panda3d.core import TextNode, LVector2i
from direct.gui.DirectLabel import DirectLabel
from yyagl.library.gui import Btn, Slider, CheckBtn, OptionMenu
from yyagl.engine.gui.page import Page, PageGui, PageFacade
from yyagl.gameobject import GameObject
from yyagl.library.gui import Label
from .thankspage import ThanksPageGui


class OptionPageProps(object):

    def __init__(self, joystick, keys, lang, volume, fullscreen, antialiasing,
                 shaders, cars_num, camera, opt_file):
        self.joystick = joystick
        self.keys = keys
        self.lang = lang
        self.volume = volume
        self.fullscreen = fullscreen
        self.antialiasing = antialiasing
        self.shaders = shaders
        self.cars_num = cars_num
        self.camera = camera
        self.opt_file = opt_file


class OptionPageGui(ThanksPageGui):

    def __init__(self, mediator, menu_args, option_props):
        self.vol_slider = self.fullscreen_cb = self.lang_opt = self.aa_cb = \
            self.shaders_cb = self.res_opt = self.cars_opt = self.cam_opt = None
        self.props = option_props
        ThanksPageGui.__init__(self, mediator, menu_args)

    def build(self):
        menu_args = self.menu_args
        widgets = [self.__add_lab('Language', _('Language'), .85)]
        langs = [lan[0] for lan in self.eng.languages]
        self.lang_opt = OptionMenu(
            text='', items=langs, pos=(.29, 1, .85),
            initialitem=self.props.lang, command=self.__change_lang,
            **menu_args.option_args)
        widgets += [self.__add_lab('Volume', _('Volume'), .65)]
        self.vol_slider = Slider(
            pos=(.32, 0, .68), scale=.49, value=self.props.volume,
            frameColor=menu_args.btn_color,
            thumb_frameColor=menu_args.text_active,
            command=lambda: self.eng.set_volume(self.vol_slider['value']))
        widgets += [self.__add_lab('Fullscreen', _('Fullscreen'), .45)]
        self.fullscreen_cb = CheckBtn(
            pos=(-.08, 1, .47), text='', indicatorValue=self.props.fullscreen,
            indicator_frameColor=menu_args.text_active,
            command=lambda val: self.eng.toggle_fullscreen(),
            **menu_args.checkbtn_args)
        widgets += [self.__add_lab('Resolution', _('Resolution'), .25)]
        res2vec = lambda res: LVector2i(*[int(val) for val in res.split('x')])
        self.res_opt = OptionMenu(
            text='',
            items=['x'.join([str(el_res) for el_res in res])
                   for res in self.eng.resolutions],
            pos=(.29, 1, .25),
            initialitem='x'.join(str(res) for res in self.eng.closest_resolution),
            command=lambda res: self.eng.set_resolution(res2vec(res)),
            **menu_args.option_args
            )
        widgets += [self.__add_lab('Antialiasing', _('Antialiasing'), .05)]
        widgets += [
            self.__add_lab('(from the next execution)',
                           _('(from the next execution)'), .05, 0,
                           TextNode.ALeft, .06)]
        self.aa_cb = CheckBtn(
            pos=(-.08, 1, .08), text='',
            indicatorValue=self.props.antialiasing,
            indicator_frameColor=menu_args.text_active, **menu_args.checkbtn_args)
        widgets += [self.__add_lab('Shaders', _('Shaders'), -.15)]
        self.shaders_cb = CheckBtn(
            pos=(-.08, 1, -.12), text='', indicatorValue=self.props.shaders,
            indicator_frameColor=menu_args.text_active, **menu_args.checkbtn_args)
        widgets += [self.__add_lab('Cars number', _('Cars number'), -.35)]
        widgets += [self.__add_lab('Camera', _('Camera'), -.55)]
        self.cars_opt = OptionMenu(
            text='', items=[str(i) for i in range(1, 9)], pos=(.29, 1, -.35),
            initialitem=self.props.cars_num - 1, **menu_args.option_args)
        self.cameras = [_('Top'), _('Rear')]
        self.camera_codes = ['top', 'rear']

        self.cam_opt = OptionMenu(
            text='', items=self.cameras, pos=(.29, 1, -.55),
            initialitem=self.cameras[self.camera_codes.index(self.props.camera)],
            **menu_args.option_args)
        input_btn = Btn(
            text='', pos=(-.2, 1, -.75), command=self.on_input_btn,
            tra_src='Configure input', tra_tra=_('Configure input'),
            **menu_args.btn_args)
        widgets += [
            self.lang_opt, self.vol_slider, self.fullscreen_cb, self.res_opt,
            self.aa_cb, input_btn, self.shaders_cb, self.cars_opt,
            self.cam_opt]
        self.add_widgets(widgets)
        idx = self.eng.lang_mgr.lang_codes.index(self.props.lang)
        self.__change_lang(self.eng.languages[idx][0])
        ThanksPageGui.build(self)

    def __add_lab(self, txt, txt_tr, pos_z, pos_x=-.3, align=TextNode.ARight,
                  scale=None):
        l_a = self.menu_args.label_args
        l_a['scale'] = scale or l_a['scale']
        lab = Label(
            text='', pos=(pos_x, 1, pos_z), text_align=align,
            tra_src=txt, tra_tra=txt_tr, **l_a)
        return lab

    def on_input_btn(self):
        opts = [self.props.joystick, self.props.opt_file['settings']['keys']]
        self.notify('on_push_page', 'input', opts)

    def translate(self):
        PageGui.translate(self)
        curr_lang = self.eng.lang_mgr.lang
        idx = [lang for lang in enumerate(self.eng.cfg.lang_cfg.languages) if lang[1][1] == curr_lang][0][0]
        self.lang_opt.set(idx, fCommand=0)

    def __change_lang(self, arg):
        code = [lang for lang in self.eng.cfg.lang_cfg.languages if lang[0] == arg][0][1]
        self.eng.lang_mgr.set_lang(code)
        self.translate()

    def _on_back(self):
        self.mediator.event.on_back()
        lang_idx = self.lang_opt.selectedIndex
        dct = {
            'lang': self.eng.languages[lang_idx][1].lower(),
            'volume': self.mediator.gui.vol_slider.get_value(),
            'fullscreen': self.mediator.gui.fullscreen_cb['indicatorValue'],
            'resolution': self.mediator.gui.res_opt.get().replace('x', ' '),
            'antialiasing': self.mediator.gui.aa_cb['indicatorValue'],
            'shaders': self.mediator.gui.shaders_cb['indicatorValue'],
            'cars_number': int(self.mediator.gui.cars_opt.get()),
            'camera': self.camera_codes[self.cameras.index(self.mediator.gui.cam_opt.get())]}
        self.notify('on_back', 'options_page', [dct])


class OptionPage(Page):
    gui_cls = OptionPageGui

    def __init__(self, menu_args, option_props):
        self.menu_args = menu_args
        init_lst = [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [self, self.menu_args, option_props])]]
        GameObject.__init__(self, init_lst)
        PageFacade.__init__(self)
        # invoke Page's __init__

    def destroy(self):
        GameObject.destroy(self)
        PageFacade.destroy(self)
