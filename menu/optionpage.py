from direct.gui.DirectCheckButton import DirectCheckButton
from direct.gui.DirectGuiGlobals import FLAT, DISABLED
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectOptionMenu import DirectOptionMenu
from direct.gui.DirectSlider import DirectSlider
from direct.gui.DirectDialog import OkDialog
from panda3d.core import TextNode
from racing.game.engine.gui.page import Page, PageEvent, PageGui


class OptionEvent(PageEvent):

    def on_back(self):
        # are these needed?
        car = game.options['car'] if 'car' in game.options.dct else ''
        track = game.options['track'] if 'track' in game.options.dct else ''
        conf = game.options
        lang_idx = self.mdt.gui._lang_opt.selectedIndex
        conf['lang'] = eng.lang_mgr.languages[lang_idx][:2].lower()
        conf['volume'] = self.mdt.gui._vol_slider.getValue()
        conf['fullscreen'] = self.mdt.gui._fullscreen_cb['indicatorValue']
        conf['resolution'] = self.mdt.gui._res_opt.get().replace('x', ' ')
        conf['aa'] = self.mdt.gui._aa_cb['indicatorValue']
        browser = self.mdt.gui._browser_cb['indicatorValue']
        conf['open_browser_at_exit'] = browser
        conf['multithreaded_render'] = game.options['multithreaded_render']
        conf['car'] = car
        conf['track'] = track
        conf.store()


class OptionPageGui(PageGui):

    def __init__(self, mdt, menu):
        self._vol_slider = None
        self._fullscreen_cb = None
        self._lang_opt = None
        self._aa_cb = None
        self._res_opt = None
        self._browser_cb = None
        PageGui.__init__(self, mdt, menu)

    def build_page(self):
        conf = game.options
        menu_gui = self.menu.gui
        menu_args = self.menu.gui.menu_args

        lang_lab = DirectLabel(
            text='', pos=(-.1, 1, .5), text_align=TextNode.ARight,
            **menu_gui.label_args)
        PageGui.transl_text(lang_lab, 'Language')
        self._lang_opt = DirectOptionMenu(
            text='', items=eng.lang_mgr.languages, pos=(.2, 1, .5),
            initialitem=conf['lang'], command=self.__change_lang,
            **menu_gui.option_args)
        vol_lab = DirectLabel(
            text='', pos=(-.1, 1, .3), text_align=TextNode.ARight,
            **menu_gui.label_args)
        PageGui.transl_text(vol_lab, 'Volume')
        self._vol_slider = DirectSlider(
            pos=(.47, 0, .33), scale=.47, value=conf['volume'],
            frameColor=menu_args.btn_color, thumb_frameColor=(.4, .4, .4, 1))

        fullscreen_lab = DirectLabel(
            text='', pos=(-.1, 1, .1), text_align=TextNode.ARight,
            **menu_gui.label_args)
        PageGui.transl_text(fullscreen_lab, 'Fullscreen')
        self._fullscreen_cb = DirectCheckButton(
            pos=(.12, 1, .12), text='',
            indicatorValue=conf['fullscreen'],
            indicator_frameColor=menu_args.btn_color,
            command=eng.gui.toggle_fullscreen, **menu_gui.checkbtn_args)

        res_lab = DirectLabel(
            text='', pos=(-.1, 1, -.1), text_align=TextNode.ARight,
            **menu_gui.label_args)
        PageGui.transl_text(res_lab, 'Resolution')
        self._res_opt = DirectOptionMenu(
            text='',
            items=['x'.join([str(el_res) for el_res in res])
                   for res in eng.gui.resolutions],
            pos=(.2, 1, -.1),
            initialitem='x'.join(str(res) for res in eng.gui.closest_res),
            command=eng.gui.set_resolution, **menu_gui.option_args)

        aa_lab = DirectLabel(
            text='', pos=(-.1, 1, -.3), text_align=TextNode.ARight,
            **menu_gui.label_args)
        PageGui.transl_text(aa_lab, 'Antialiasing')
        aa_next_lab = DirectLabel(
            text='', pos=(.2, 1, -.3), text_align=TextNode.ALeft,
            **menu_gui.label_args)
        PageGui.transl_text(aa_next_lab, '(from the next execution)')
        self._aa_cb = DirectCheckButton(
            pos=(.12, 1, -.27), text='', indicatorValue=conf['aa'],
             **menu_gui.checkbtn_args)

        browser_lab = DirectLabel(
            text='', pos=(-.1, 1, -.5), text_align=TextNode.ARight,
             **menu_gui.label_args)
        PageGui.transl_text(browser_lab, "See Ya2's news at exit")
        self._browser_cb = DirectCheckButton(
            pos=(.12, 1, -.47), text='',
            indicatorValue=conf['open_browser_at_exit'],
            command=self.on_browser, **menu_gui.checkbtn_args)

        if eng.logic.is_runtime:
            fullscreen_lab['text_fg'] = (.75, .75, .75, 1)
            self.__fullscreen_cb['state'] = DISABLED
            self.__res_opt['text_fg'] = (.75, .75, .75, 1)
            self.__res_opt['state'] = DISABLED

        self.widgets += [
            lang_lab, self._lang_opt, vol_lab, self._vol_slider,
            fullscreen_lab, self._fullscreen_cb, res_lab, self._res_opt,
            aa_lab, self._aa_cb, aa_next_lab, browser_lab, self._browser_cb]
        idx = eng.lang_mgr.lang_codes.index(conf['lang'])
        self.__change_lang(eng.lang_mgr.languages[idx])
        PageGui.build_page(self)

    def on_browser(self, val):
        txt = _('Please, really consider enabling this option to see our news.'
                '\nWe hope you will find interesting stuff there.\nMoreover, '
                'this is how we can keep Yorg free.')
        if not val:
            dial = OkDialog(dialogName="Ya2's news", text=txt,
                            frameColor=self.menu.gui.menu_args.dial_color)
            dial['command'] = lambda val: dial.cleanup()  # it destroys too

    def update_texts(self):
        PageGui.update_texts(self)
        curr_lang = eng.lang_mgr.curr_lang
        self._lang_opt.set({'en': 0, 'it': 1}[curr_lang], fCommand=0)

    def __change_lang(self, arg):
        lang_dict = {'English': 'en', 'Italiano': 'it'}
        eng.lang_mgr.set_lang(lang_dict[arg])
        self.update_texts()


class OptionPage(Page):
    gui_cls = OptionPageGui
    event_cls = OptionEvent
