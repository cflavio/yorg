from direct.gui.DirectButton import DirectButton
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectEntry
from yyagl.engine.gui.page import Page, PageEvent
from yyagl.engine.network.client import ClientError, Client
from .carpage import CarPageClient
from .netmsgs import NetMsgs
from .thankspage import ThanksPageGui


class ClientEvent(PageEvent):

    def on_back(self):
        if Client().is_active:
            Client().destroy()

    def process_msg(self, data_lst, sender):
        if data_lst[0] == NetMsgs.track_selected:
            eng.log('track selected: ' + data_lst[1])
            self.mdt.gui.menu.track = data_lst[1]
            self.mdt.gui.menu.push_page(CarPageClient(self.mdt.gui.menu))


class ClientPageGui(ThanksPageGui):

    def __init__(self, mdt, menu):
        self.ent = None
        ThanksPageGui.__init__(self, mdt, menu)

    def build_page(self):
        menu_gui = self.mdt.menu.gui
        menu_args = self.mdt.menu.gui.menu_args
        txt = OnscreenText(text=_('Client'), pos=(0, .4), **menu_gui.menu_args.text_args)
        widgets = [txt]
        self.ent = DirectEntry(
            scale=.12, pos=(-.68, 1, .2), entryFont=menu_args.font, width=12,
            frameColor=menu_args.btn_color,
            initialText=_('insert the server address'))
        self.ent.onscreenText['fg'] = menu_args.text_fg
        btn = DirectButton(text=_('Connect'), pos=(0, 1, -.2),
                           command=self.connect, **menu_gui.menu_args.btn_args)
        widgets += [self.ent, btn]
        map(self.add_widget, widgets)
        ThanksPageGui.build_page(self)

    def connect(self):
        menu_gui = self.mdt.menu.gui
        try:
            eng.log(self.ent.get())
            Client().start(self.mdt.event.process_msg, self.ent.get())
            menu_args = self.mdt.menu.gui.menu_args
            self.add_widget(OnscreenText(
                text=_('Waiting for the server'), scale=.12, pos=(0, -.5),
                font=menu_gui.font, fg=menu_args.text_fg))
        except ClientError:
            txt = OnscreenText(_('Error'), pos=(0, -.05), fg=(1, 0, 0, 1),
                               scale=.16, font=menu_gui.menu_args.font)
            eng.do_later(5, txt.destroy)


class ClientPage(Page):
    gui_cls = ClientPageGui
    event_cls = ClientEvent

    def __init__(self, menu_args, menu):
        self.menu_args = menu_args
        self.menu = menu
        Page.__init__(self, self.menu_args, self.menu)
