from panda3d.core import TextNode, LVector2i
from direct.gui.DirectCheckButton import DirectCheckButton
from direct.gui.DirectGuiGlobals import DISABLED
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectOptionMenu import DirectOptionMenu
from direct.gui.DirectSlider import DirectSlider
from direct.gui.DirectButton import DirectButton
from yyagl.engine.gui.page import Page, PageEvent, PageGui
from yyagl.engine.lang import LangMgr
from yyagl.gameobject import GameObject
from .inputpage import InputPage
from .thankspage import ThanksPageGui


class OptionPageProps(object):

    def __init__(self, joystick, keys, lang, volume, fullscreen, aa, opt_file):
        self.joystick = joystick
        self.keys = keys
        self.lang = lang
        self.volume = volume
        self.fullscreen = fullscreen
        self.aa = aa
        self.opt_file = opt_file


class OptionEvent(PageEvent):

    def on_back(self):
        lang_idx = self.mdt.gui._lang_opt.selectedIndex
        dct = {
            'lang': eng.languages[lang_idx][:2].lower(),
            'volume': self.mdt.gui._vol_slider.getValue(),
            'fullscreen': self.mdt.gui._fullscreen_cb['indicatorValue'],
            'resolution': self.mdt.gui._res_opt.get().replace('x', ' '),
            'aa': self.mdt.gui._aa_cb['indicatorValue']}
        self.mdt.menu.gui.notify('on_options_back', dct)


class OptionPageGui(ThanksPageGui):

    def __init__(self, mdt, menu_args, option_props):
        self._vol_slider = None
        self._fullscreen_cb = None
        self._lang_opt = None
        self._aa_cb = None
        self._res_opt = None
        self._browser_cb = None
        self.props = option_props
        ThanksPageGui.__init__(self, mdt, menu_args)

    def bld_page(self):
        menu_args = self.menu_args
        self.pagewidgets = []

        def add_lab(txt, txt_tr, z):
            lab = DirectLabel(
                text='', pos=(-.1, 1, z), text_align=TextNode.ARight,
                **menu_args.label_args)
            PageGui.transl_text(lab, txt, txt_tr)
            self.pagewidgets += [lab]
            return lab
        add_lab('Language', _('Language'), .5)
        self._lang_opt = DirectOptionMenu(
            text='', items=eng.languages, pos=(.49, 1, .5),
            initialitem=self.props.lang, command=self.__change_lang,
            **menu_args.option_args)
        add_lab('Volume', _('Volume'), .3)
        self._vol_slider = DirectSlider(
            pos=(.52, 0, .33), scale=.49, value=self.props.volume,
            frameColor=menu_args.btn_color, thumb_frameColor=menu_args.text_fg,
            command=self.__on_volume)
        fullscreen_lab = add_lab('Fullscreen', _('Fullscreen'), .1)
        self._fullscreen_cb = DirectCheckButton(
            pos=(.12, 1, .12), text='', indicatorValue=self.props.fullscreen,
            indicator_frameColor=menu_args.text_fg,
            command=lambda val: eng.toggle_fullscreen(),
            **menu_args.checkbtn_args)
        add_lab('Resolution', _('Resolution'), -.1)
        res2vec = lambda res: LVector2i(*[int(val) for val in res.split('x')])
        self._res_opt = DirectOptionMenu(
            text='',
            items=['x'.join([str(el_res) for el_res in res])
                   for res in eng.resolutions],
            pos=(.49, 1, -.1),
            initialitem='x'.join(str(res) for res in eng.closest_res),
            command=lambda res: eng.set_resolution(res2vec(res)),
            **menu_args.option_args)
        add_lab('Antialiasing', _('Antialiasing'), -.3)
        aa_next_lab = DirectLabel(
            text='', pos=(.2, 1, -.3), text_align=TextNode.ALeft,
            **menu_args.label_args)
        PageGui.transl_text(aa_next_lab, '(from the next execution)',
                            _('(from the next execution)'))
        self._aa_cb = DirectCheckButton(
            pos=(.12, 1, -.27), text='', indicatorValue=self.props.aa,
            indicator_frameColor=menu_args.text_fg, **menu_args.checkbtn_args)
        #bld_in = lambda: self.menu.logic.push_page(
        #    InputPage(self.menu, self.props.joystick, self.props.keys))
        # it doesn't work if we go forward and back between options and input:
        # we should update keys
        input_btn = DirectButton(
            text='', pos=(0, 1, -.5), command=self.on_input_btn, **menu_args.btn_args)
        PageGui.transl_text(input_btn, 'Configure input', _('Configure input'))

        self.pagewidgets += [
            self._lang_opt, self._vol_slider, self._fullscreen_cb,
            self._res_opt, self._aa_cb, aa_next_lab, input_btn]
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
        self._lang_opt.set({'en': 0, 'it': 1}[curr_lang], fCommand=0)

    def __on_volume(self):
        eng.set_volume(self._vol_slider['value'])

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
