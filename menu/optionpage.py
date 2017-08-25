from panda3d.core import TextNode, LVector2i
from direct.gui.DirectCheckButton import DirectCheckButton
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectOptionMenu import DirectOptionMenu
from direct.gui.DirectSlider import DirectSlider
from direct.gui.DirectButton import DirectButton
from yyagl.engine.gui.page import Page, PageEvent, PageGui, PageFacade
from yyagl.engine.lang import LangMgr
from yyagl.gameobject import GameObject
from .inputpage import InputPage
from .thankspage import ThanksPageGui


class OptionPageProps(object):

    def __init__(self, joystick, keys, lang, volume, fullscreen, antialiasing,
                 shaders, cars_num, opt_file):
        self.joystick = joystick
        self.keys = keys
        self.lang = lang
        self.volume = volume
        self.fullscreen = fullscreen
        self.antialiasing = antialiasing
        self.shaders = shaders
        self.cars_num = cars_num
        self.opt_file = opt_file


class OptionEvent(PageEvent):

    def on_back(self):
        lang_idx = self.mdt.gui.lang_opt.selectedIndex
        dct = {
            'lang': eng.languages[lang_idx][:2].lower(),
            'volume': self.mdt.gui.vol_slider.getValue(),
            'fullscreen': self.mdt.gui.fullscreen_cb['indicatorValue'],
            'resolution': self.mdt.gui.res_opt.get().replace('x', ' '),
            'antialiasing': self.mdt.gui.aa_cb['indicatorValue'],
            'shaders': self.mdt.gui.shaders_cb['indicatorValue'],
            'cars_number': int(self.mdt.gui.cars_opt.get())}
        self.mdt.menu.gui.notify('on_options_back', dct)


class OptionPageGui(ThanksPageGui):

    def __init__(self, mdt, menu_args, option_props):
        self.vol_slider = None
        self.fullscreen_cb = None
        self.lang_opt = None
        self.aa_cb = None
        self.shaders_cb = None
        self.res_opt = None
        self.cars_opt = None
        self.props = option_props
        ThanksPageGui.__init__(self, mdt, menu_args)

    def bld_page(self):
        menu_args = self.menu_args
        self.pagewidgets = []

        def add_lab(txt, txt_tr, pos_z):
            lab = DirectLabel(
                text='', pos=(-.1, 1, pos_z), text_align=TextNode.ARight,
                **menu_args.label_args)
            PageGui.transl_text(lab, txt, txt_tr)
            self.pagewidgets += [lab]
            return lab
        add_lab('Language', _('Language'), .85)
        self.lang_opt = DirectOptionMenu(
            text='', items=eng.languages, pos=(.49, 1, .85),
            initialitem=self.props.lang, command=self.__change_lang,
            **menu_args.option_args)
        add_lab('Volume', _('Volume'), .65)
        self.vol_slider = DirectSlider(
            pos=(.52, 0, .68), scale=.49, value=self.props.volume,
            frameColor=menu_args.btn_color, thumb_frameColor=menu_args.text_fg,
            command=self.__on_volume)
        add_lab('Fullscreen', _('Fullscreen'), .45)
        self.fullscreen_cb = DirectCheckButton(
            pos=(.12, 1, .47), text='', indicatorValue=self.props.fullscreen,
            indicator_frameColor=menu_args.text_fg,
            command=lambda val: eng.toggle_fullscreen(),
            **menu_args.checkbtn_args)
        add_lab('Resolution', _('Resolution'), .25)
        res2vec = lambda res: LVector2i(*[int(val) for val in res.split('x')])
        self.res_opt = DirectOptionMenu(
            text='',
            items=['x'.join([str(el_res) for el_res in res])
                   for res in eng.resolutions],
            pos=(.49, 1, .25),
            initialitem='x'.join(str(res) for res in eng.closest_res),
            command=lambda res: eng.set_resolution(res2vec(res)),
            **menu_args.option_args)
        add_lab('Antialiasing', _('Antialiasing'), .05)
        aa_next_lab = DirectLabel(
            text='', pos=(.2, 1, .05), text_align=TextNode.ALeft,
            **menu_args.label_args)
        PageGui.transl_text(aa_next_lab, '(from the next execution)',
                            _('(from the next execution)'))
        self.aa_cb = DirectCheckButton(
            pos=(.12, 1, .08), text='', indicatorValue=self.props.antialiasing,
            indicator_frameColor=menu_args.text_fg, **menu_args.checkbtn_args)
        add_lab('Shaders', _('Shaders'), -.15)
        self.shaders_cb = DirectCheckButton(
            pos=(.12, 1, -.12), text='', indicatorValue=self.props.shaders,
            indicator_frameColor=menu_args.text_fg, **menu_args.checkbtn_args)
        add_lab('Cars number', _('Cars number'), -.35)
        self.cars_opt = DirectOptionMenu(
            text='',
            items=[str(i) for i in range(1, 9)],
            pos=(.49, 1, -.35),
            initialitem=self.props.cars_num - 1,
            **menu_args.option_args)
        # bld_in = lambda: self.menu.logic.push_page(
        #     InputPage(self.menu, self.props.joystick, self.props.keys))
        # it doesn't work if we go forward and back between options and input:
        # we should update keys
        input_btn = DirectButton(
            text='', pos=(0, 1, -.55), command=self.on_input_btn,
            **menu_args.btn_args)
        PageGui.transl_text(input_btn, 'Configure input', _('Configure input'))

        self.pagewidgets += [
            self.lang_opt, self.vol_slider, self.fullscreen_cb,
            self.res_opt, self.aa_cb, aa_next_lab, input_btn,
            self.shaders_cb, self.cars_opt]
        map(self.add_widget, self.pagewidgets)
        idx = LangMgr().lang_codes.index(self.props.lang)
        self.__change_lang(eng.languages[idx])
        ThanksPageGui.bld_page(self)

    def on_input_btn(self):
        input_page = InputPage(
            self.menu_args, self.props.joystick,
            self.props.opt_file['settings']['keys'], self.mdt.menu)
        self.notify('on_push_page', input_page)

    def update_texts(self):
        PageGui.update_texts(self)
        curr_lang = LangMgr().curr_lang
        self.lang_opt.set({'en': 0, 'it': 1}[curr_lang], fCommand=0)

    def __on_volume(self):
        eng.set_volume(self.vol_slider['value'])

    def __change_lang(self, arg):
        lang_dict = {'English': 'en', 'Italiano': 'it'}
        LangMgr().set_lang(lang_dict[arg])
        self.update_texts()


class OptionPage(Page):
    gui_cls = OptionPageGui
    event_cls = OptionEvent

    def __init__(self, menu_args, option_props, menu):
        self.menu_args = menu_args
        self.menu = menu
        init_lst = [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [self, self.menu_args, option_props])]]
        GameObject.__init__(self, init_lst)
        PageFacade.__init__(self)
