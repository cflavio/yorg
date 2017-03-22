from panda3d.core import TextNode, LVector2i
from direct.gui.DirectCheckButton import DirectCheckButton
from direct.gui.DirectGuiGlobals import DISABLED
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectOptionMenu import DirectOptionMenu
from direct.gui.DirectSlider import DirectSlider
from direct.gui.DirectButton import DirectButton
from yyagl.engine.gui.page import Page, PageEvent, PageGui
from yyagl.gameobject import GameObjectMdt
from .inputpage import InputPage
from .thankspage import ThanksPageGui


class OptionEvent(PageEvent):

    def on_back(self):
        lang_idx = self.mdt.gui._lang_opt.selectedIndex
        dct = {
            'lang': eng.logic.cfg.languages[lang_idx][:2].lower(),
            'volume': self.mdt.gui._vol_slider.getValue(),
            'fullscreen': self.mdt.gui._fullscreen_cb['indicatorValue'],
            'resolution': self.mdt.gui._res_opt.get().replace('x', ' '),
            'aa': self.mdt.gui._aa_cb['indicatorValue']}
        self.mdt.menu.gui.notify('on_options_back', dct)


class OptionPageGui(ThanksPageGui):

    def __init__(self, mdt, menu, joystick, keys, lang, volume, fullscreen,
                 aa):
        self._vol_slider = None
        self._fullscreen_cb = None
        self._lang_opt = None
        self._aa_cb = None
        self._res_opt = None
        self._browser_cb = None
        self.joystick = joystick
        self.keys = keys
        self.lang = lang
        self.volume = volume
        self.fullscreen = fullscreen
        self.aa = aa
        ThanksPageGui.__init__(self, mdt, menu)

    def build_page(self):
        menu_gui = self.menu.gui
        menu_args = self.menu.gui.menu_args

        lang_lab = DirectLabel(
            text='', pos=(-.1, 1, .5), text_align=TextNode.ARight,
            **menu_gui.label_args)
        PageGui.transl_text(lang_lab, 'Language', _('Language'))
        self._lang_opt = DirectOptionMenu(
            text='', items=eng.languages, pos=(.49, 1, .5),
            initialitem=self.lang, command=self.__change_lang,
            **menu_gui.option_args)
        vol_lab = DirectLabel(
            text='', pos=(-.1, 1, .3), text_align=TextNode.ARight,
            **menu_gui.label_args)
        PageGui.transl_text(vol_lab, 'Volume', _('Volume'))
        self._vol_slider = DirectSlider(
            pos=(.52, 0, .33), scale=.49, value=self.volume,
            frameColor=menu_args.btn_color, thumb_frameColor=menu_args.text_fg)

        fullscreen_lab = DirectLabel(
            text='', pos=(-.1, 1, .1), text_align=TextNode.ARight,
            **menu_gui.label_args)
        PageGui.transl_text(fullscreen_lab, 'Fullscreen', _('Fullscreen'))
        self._fullscreen_cb = DirectCheckButton(
            pos=(.12, 1, .12), text='',
            indicatorValue=self.fullscreen,
            indicator_frameColor=menu_args.text_fg,
            command=lambda val: eng.toggle_fullscreen(),
            **menu_gui.checkbtn_args)

        res_lab = DirectLabel(
            text='', pos=(-.1, 1, -.1), text_align=TextNode.ARight,
            **menu_gui.label_args)
        PageGui.transl_text(res_lab, 'Resolution', _('Resolution'))
        res2vec = lambda res: LVector2i(*[int(val) for val in res.split('x')])
        self._res_opt = DirectOptionMenu(
            text='',
            items=['x'.join([str(el_res) for el_res in res])
                   for res in eng.resolutions],
            pos=(.49, 1, -.1),
            initialitem='x'.join(str(res) for res in eng.gui.closest_res),
            command=lambda res: eng.gui.set_resolution(res2vec(res)),
            **menu_gui.option_args)

        aa_lab = DirectLabel(
            text='', pos=(-.1, 1, -.3), text_align=TextNode.ARight,
            **menu_gui.label_args)
        PageGui.transl_text(aa_lab, 'Antialiasing', _('Antialiasing'))
        aa_next_lab = DirectLabel(
            text='', pos=(.2, 1, -.3), text_align=TextNode.ALeft,
            **menu_gui.label_args)
        PageGui.transl_text(aa_next_lab, '(from the next execution)',
                            _('(from the next execution)'))
        self._aa_cb = DirectCheckButton(
            pos=(.12, 1, -.27), text='', indicatorValue=self.aa,
            indicator_frameColor=menu_args.text_fg,
            **menu_gui.checkbtn_args)

        bld_in = lambda: self.menu.logic.push_page(
            InputPage(self.menu, self.joystick, self.keys))
        input_btn = DirectButton(
            text='', pos=(0, 1, -.5),
            command=bld_in,
            **menu_gui.btn_args)
        PageGui.transl_text(input_btn, 'Configure input', _('Configure input'))

        if eng.logic.is_runtime:
            fullscreen_lab['text_fg'] = menu_args.text_bg,
            self.__fullscreen_cb['state'] = DISABLED
            self.__res_opt['text_fg'] = menu_args.text_bg,
            self.__res_opt['state'] = DISABLED

        widgets = [
            lang_lab, self._lang_opt, vol_lab, self._vol_slider,
            fullscreen_lab, self._fullscreen_cb, res_lab, self._res_opt,
            aa_lab, self._aa_cb, aa_next_lab, input_btn]
        map(self.add_widget, widgets)
        idx = eng.lang_codes.index(self.lang)
        self.__change_lang(eng.languages[idx])
        ThanksPageGui.build_page(self)

    def update_texts(self):
        PageGui.update_texts(self)
        curr_lang = eng.curr_lang
        self._lang_opt.set({'en': 0, 'it': 1}[curr_lang], fCommand=0)

    def __change_lang(self, arg):
        lang_dict = {'English': 'en', 'Italiano': 'it'}
        eng.set_lang(lang_dict[arg])
        self.update_texts()


class OptionPage(Page):
    gui_cls = OptionPageGui
    event_cls = OptionEvent

    def __init__(self, menu, joystick, keys, lang, volume, fullscreen, aa):
        self.menu = menu
        init_lst = [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [self, self.menu, joystick, keys, lang,
                                    volume, fullscreen, aa])]]
        GameObjectMdt.__init__(self, init_lst)
