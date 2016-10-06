'''This module provides a GUI page.'''
from direct.gui.DirectButton import DirectButton
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import TextNode
from .imgbtn import ImageButton
from ..gameobject import GameObjectMdt, Gui, Event


class PageArgs(object):
    '''This class models the arguments of a page.'''

    def __init__(
            self, fsm, font, btn_size, btn_color, back, social, version,
            back_state, dial_color, background, rollover, click, social_path):
        self.fsm = fsm
        self.font = font
        self.btn_size = btn_size
        self.btn_color = btn_color
        self.back = back
        self.social = social
        self.version = version
        self.back_state = back_state
        self.dial_color = dial_color
        self.background = background
        self.rollover = rollover
        self.click = click
        self.social_path = social_path


class PageGui(Gui):
    '''This class models the GUI component of a page.'''

    def __init__(self, mdt, page_args):
        Gui.__init__(self, mdt)
        self.page_args = page_args
        self.font = eng.font_mgr.load_font(page_args.font)
        self.background = None
        self.widgets = []

    def build(self):
        '''Builds a page.'''
        self.update_texts()
        if self.page_args.back:
            self.__build_back_btn()
        if self.page_args.social:
            self.__build_social()
        if self.page_args.version:
            self.__build_version()
        self.background = OnscreenImage(scale=(1.77778, 1, 1.0),
                                        image=self.page_args.background)
        self.background.setBin('background', 10)
        self.widgets += [self.background]

    @staticmethod
    def transl_text(obj, text_src):
        '''We get text_src to put it into po files.'''
        obj.__text_src = text_src
        obj.__class__.transl_text = property(lambda self: _(self.__text_src))

    def update_texts(self):
        '''Updates the texts.'''
        tr_wdg = [wdg for wdg in self.widgets if hasattr(wdg, 'transl_text')]
        for wdg in tr_wdg:
            wdg['text'] = wdg.transl_text

    def __build_back_btn(self):
        '''Sets the back button.'''
        page_args = self.page_args
        self.widgets += [DirectButton(
            text='', scale=.12, pos=(0, 1, -.8), text_font=self.font,
            text_fg=(.75, .75, .75, 1), command=self.__on_back,
            frameColor=page_args.btn_color, frameSize=page_args.btn_size,
            rolloverSound=loader.loadSfx(page_args.rollover),
            clickSound=loader.loadSfx(page_args.click))]
        PageGui.transl_text(self.widgets[-1], 'Back')
        self.widgets[-1]['text'] = self.widgets[-1].transl_text

    def __on_back(self):
        '''Called when the user presses back.'''
        self.mdt.event.on_back()
        self.page_args.fsm.demand(self.page_args.back_state)

    def __build_social(self):
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
                image=self.page_args.social_path % site[0],
                command=eng.open_browser, extraArgs=[site[1]],
                rolloverSound=loader.loadSfx(self.page_args.rollover),
                clickSound=loader.loadSfx(self.page_args.click))
            for i, site in enumerate(sites)]

    def __build_version(self):
        '''Sets the version.'''
        self.widgets += [OnscreenText(
            text=eng.version, parent=eng.a2dBottomLeft, pos=(.02, .02),
            scale=.04, fg=(.8, .8, .8, 1), align=TextNode.ALeft,
            font=self.font)]

    def destroy(self):
        '''Destroys the page.'''
        map(lambda wdg: wdg.destroy(), self.widgets)


class PageEvent(Event):
    '''This class models the 'event' component of a page.'''

    def on_back(self):
        '''Pseudoabstract method.'''
        pass


class Page(GameObjectMdt):
    '''This class models a page.'''
    gui_cls = PageGui
    event_cls = PageEvent

    def __init__(self, page_args):
        self.fsm = self.fsm_cls(self)
        self.gfx = self.gfx_cls(self)
        self.phys = self.phys_cls(self)
        self.gui = self.gui_cls(self, page_args)
        self.logic = self.logic_cls(self)
        self.audio = self.audio_cls(self)
        self.ai = self.ai_cls(self)
        self.event = self.event_cls(self)
