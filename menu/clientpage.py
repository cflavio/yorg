from direct.gui.DirectButton import DirectButton
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectEntry
from yyagl.engine.gui.page import Page, PageEvent
from yyagl.engine.network.network import NetworkError
from .netmsgs import NetMsgs
from .thankspage import ThanksPageGui


class ClientEvent(PageEvent):

    def on_back(self):
        if self.eng.client.is_active:
            self.eng.client.destroy()

    def process_msg(self, data_lst, sender):
        if data_lst[0] == NetMsgs.track_selected:
            self.eng.log_mgr.log('track selected: ' + data_lst[1])
            self.notify('on_track_selected', data_lst[1])
            self.mediator.gui.notify('on_push_page', 'carpageclient',
                                [self.mediator.gui.props])


class ClientPageGui(ThanksPageGui):

    def __init__(self, mediator, props):
        self.ent = None
        self.props = props
        ThanksPageGui.__init__(self, mediator, props.gameprops.menu_args)

    def build(self):
        menu_args = self.props.gameprops.menu_args
        txt = OnscreenText(text=_('Client'), pos=(0, .4),
                           **menu_args.text_args)
        self.ent = DirectEntry(
            scale=.12, pos=(-.68, 1, .2), entryFont=menu_args.font, width=12,
            frameColor=menu_args.btn_color,
            initialText='192.168.1.102')
        self.ent.onscreenText['fg'] = menu_args.text_active
        btn = DirectButton(text=_('Connect'), pos=(0, 1, -.2),
                           command=self.connect, **menu_args.btn_args)
        self.add_widgets([txt, self.ent, btn])
        ThanksPageGui.build(self)

    def connect(self):
        menu_args = self.props.gameprops.menu_args
        try:
            self.eng.log_mgr.log(self.ent.get())
            self.eng.client.start(self.mediator.event.process_msg, self.ent.get())
            wait_txt = OnscreenText(
                text=_('Waiting for the server'), scale=.12, pos=(0, -.5),
                font=menu_args.font, fg=menu_args.text_active)
            self.add_widgets([wait_txt])
        except NetworkError:
            txt = OnscreenText(_('Error'), pos=(0, -.05), fg=(1, 0, 0, 1),
                               scale=.16, font=menu_args.font)
            self.eng.do_later(5, txt.destroy)


class ClientPage(Page):
    gui_cls = ClientPageGui
    event_cls = ClientEvent

    def __init__(self, menu_args):
        self.menu_args = menu_args
        Page.__init__(self, self.menu_args)
