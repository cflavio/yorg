'''This module provides a GUI page.'''
from direct.gui.DirectButton import DirectButton
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode
from direct.gui.OnscreenImage import OnscreenImage
from .imgbtn import ImageButton
from ..gameobject import GameObjectMdt, Gui


def transl_text(obj, text_src):
    '''We get text_transl to put it into po files.'''
    obj.__text_src = text_src
    obj.__class__.transl_text = property(lambda self: _(self.__text_src))


def may_destroy(wdg):
    '''Possibly destroy a widget.'''
    try:
        wdg.destroy()
    except AttributeError:  # wdg may be None
        pass


class PageArgs(object):
    '''This class models the arguments of a page.'''

    def __init__(self, fsm, font, btn_size, btn_color, back, social, version,
                 back_state, dial_color):
        self.fsm = fsm
        self.font = font
        self.btn_size = btn_size
        self.btn_color = btn_color
        self.back = back
        self.social = social
        self.version = version
        self.back_state = back_state
        self.dial_color = dial_color


class PageGui(Gui):
    '''This class models the GUI component of a page.'''

    def __init__(self, mdt, page_args):
        Gui.__init__(self, mdt)
        self.page_args = page_args
        self.font = eng.font_mgr.load_font(page_args.font)
        self.background = None

    def create(self):
        '''Creates a page.'''
        self.update_texts()
        if self.page_args.back:
            self.__set_back_btn()
        if self.page_args.social:
            self.__set_social()
        if self.page_args.version:
            self.__set_version()
        self.background = OnscreenImage(
            scale=(1.77778, 1, 1.0),
            image='assets/images/gui/menu_background.jpg')
        self.background.setBin('background', 10)
        self.widgets += [self.background]

    def update_texts(self):
        '''Updates the texts.'''
        tr_wdg = [wdg for wdg in self.widgets if hasattr(wdg, 'transl_text')]
        for wdg in tr_wdg:
            wdg['text'] = wdg.transl_text

    def __set_back_btn(self):
        '''Sets the back button.'''
        page_args = self.page_args
        self.widgets += [DirectButton(
            text='', scale=.12, pos=(0, 1, -.8), text_font=self.font,
            text_fg=(.75, .75, .75, 1),
            frameColor=page_args.btn_color, frameSize=page_args.btn_size,
            command=self.__on_back,
            rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
            clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))]
        transl_text(self.widgets[-1], 'Back')
        self.widgets[-1]['text'] = self.widgets[-1].transl_text

    def __on_back(self):
        '''Called when the user presses back.'''
        self.on_back()
        self.page_args.fsm.demand(self.page_args.back_state)

    def on_back(self):
        '''Pseudoabstract method.'''
        pass

    def __set_social(self):
        '''Sets social buttons.'''
        sites = [
            ('facebook', 'http://www.facebook.com/Ya2Tech'),
            ('twitter', 'http://twitter.com/ya2tech'),
            ('google_plus', 'https://plus.google.com/118211180567488443153'),
            ('youtube',
             'http://www.youtube.com/user/ya2games?sub_confirmation=1'),
            ('pinterest', 'http://www.pinterest.com/ya2tech'),
            ('tumblr', 'http://ya2tech.tumblr.com'),
            ('feed', 'http://www.ya2.it/feed-following')]
        self.widgets += [
            ImageButton(
                parent=eng.a2dBottomRight, scale=.1,
                pos=(-1.0 + i*.15, 1, .1), frameColor=(0, 0, 0, 0),
                image='assets/images/icons/%s_png.png' % site[0],
                command=eng.open_browser, extraArgs=[site[1]],
                rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
                clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))
            for i, site in enumerate(sites)]

    def __set_version(self):
        '''Sets the version.'''
        self.widgets += [
            OnscreenText(text=eng.version, parent=eng.a2dBottomLeft,
                         pos=(.02, .02), scale=.04, fg=(.8, .8, .8, 1),
                         align=TextNode.ALeft, font=self.font)]

    def destroy(self):
        '''Destroys the page.'''
        map(lambda wdg: wdg.destroy(), self.widgets)


class Page(GameObjectMdt):
    '''This class models a page.'''
    gui_cls = PageGui

    def __init__(self, page_args):
        self.fsm = self.fsm_cls(self)
        self.gfx = self.gfx_cls(self)
        self.phys = self.phys_cls(self)
        self.gui = self.gui_cls(self, page_args)
        self.logic = self.logic_cls(self)
        self.audio = self.audio_cls(self)
        self.ai = self.ai_cls(self)
        self.event = self.event_cls(self)
