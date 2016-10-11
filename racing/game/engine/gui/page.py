'''This module provides a GUI page.'''
from direct.gui.DirectButton import DirectButton
from ...gameobject.gameobject import GameObjectMdt, Gui, Event


class PageGui(Gui):
    '''This class models the GUI component of a page.'''

    def __init__(self, mdt, menu):
        Gui.__init__(self, mdt)
        self.menu = menu
        self.widgets = []
        self.build()
        self.update_texts()

    def build(self):
        '''Builds a page.'''
        self.__build_back_btn()

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
        self.widgets += [DirectButton(
            text='', pos=(0, 1, -.8), command=self.__on_back,
            **self.menu.gui.btn_args)]
        PageGui.transl_text(self.widgets[-1], 'Back')
        self.widgets[-1]['text'] = self.widgets[-1].transl_text

    def __on_back(self):
        '''Called when the user presses back.'''
        self.mdt.event.on_back()
        self.notify()

    def show(self):
        '''Destroys the page.'''
        map(lambda wdg: wdg.show(), self.widgets)

    def hide(self):
        '''Destroys the page.'''
        map(lambda wdg: wdg.hide(), self.widgets)

    def destroy(self):
        '''Destroys the page.'''
        self.menu = None
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

    def __init__(self, menu):
        self.fsm = self.fsm_cls(self)
        self.gfx = self.gfx_cls(self)
        self.phys = self.phys_cls(self)
        self.gui = self.gui_cls(self, menu)
        self.logic = self.logic_cls(self)
        self.audio = self.audio_cls(self)
        self.ai = self.ai_cls(self)
        self.event = self.event_cls(self)
