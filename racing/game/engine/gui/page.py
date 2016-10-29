from direct.gui.DirectButton import DirectButton
from ...gameobject import GameObjectMdt, Gui, Event


class PageGui(Gui):

    def __init__(self, mdt, menu):
        Gui.__init__(self, mdt)
        self.menu = menu
        self.widgets = []
        self.build_page()
        self.update_texts()

    def build_page(self):
        self.__build_back_btn()

    @staticmethod
    def transl_text(obj, text_src):
        obj.__text_src = text_src
        obj.__class__.transl_text = property(lambda self: _(self.__text_src))

    def update_texts(self):
        tr_wdg = [wdg for wdg in self.widgets if hasattr(wdg, 'transl_text')]
        for wdg in tr_wdg:
            wdg['text'] = wdg.transl_text

    def __build_back_btn(self):
        self.widgets += [DirectButton(
            text='', pos=(0, 1, -.8), command=self.__on_back,
            **self.menu.gui.btn_args)]
        PageGui.transl_text(self.widgets[-1], 'Back')
        self.widgets[-1]['text'] = self.widgets[-1].transl_text

    def __on_back(self):
        self.mdt.event.on_back()
        self.notify('on_back')

    def show(self):
        map(lambda wdg: wdg.show(), self.widgets)

    def hide(self):
        map(lambda wdg: wdg.hide(), self.widgets)

    def destroy(self):
        self.menu = None
        map(lambda wdg: wdg.destroy(), self.widgets)


class PageEvent(Event):

    def on_back(self):
        pass


class Page(GameObjectMdt):
    gui_cls = PageGui
    event_cls = PageEvent

    def __init__(self, menu):
        self.fsm = self.fsm_cls(self)
        self.gfx = self.gfx_cls(self)
        self.phys = self.phys_cls(self)
        self.event = self.event_cls(self)
        self.gui = self.gui_cls(self, menu)
        self.logic = self.logic_cls(self)
        self.audio = self.audio_cls(self)
        self.ai = self.ai_cls(self)
