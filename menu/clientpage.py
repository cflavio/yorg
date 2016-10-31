from direct.gui.DirectButton import DirectButton
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectEntry
from racing.game.engine.gui.page import Page, PageGui, PageEvent
from racing.game.engine.network.client import ClientError
from .carpage import CarPage
from .netmsgs import NetMsgs


class ClientEvent(PageEvent):

    def on_back(self):
        if eng.client.is_active:
            eng.client.stop()

    def process_msg(self, data_lst, sender):
        if data_lst[0] == NetMsgs.track_selected:
            eng.log_mgr.log('track selected: ' + data_lst[1])
            self.menu.track = data_lst[1]
            self.menu.logic.push_page(CarPage(self.menu))


class ClientPageGui(PageGui):

    def __init__(self, mdt, menu):
        self.ent = None
        PageGui.__init__(self, mdt, menu)

    def build_page(self):
        menu_gui = self.menu.gui
        menu_args = self.menu.gui.menu_args
        txt = OnscreenText(text='', pos=(0, .4), **menu_gui.text_args)
        self.widgets += [txt]
        PageGui.transl_text(self.widgets[0], _('Client'))
        self.ent = DirectEntry(
            scale=.12, pos=(-.68, 1, .2), entryFont=menu_gui.font, width=12,
            frameColor=menu_args.btn_color,
            initialText='insert the server address')
        self.ent.onscreenText['fg'] = (.75, .75, .75, 1)
        self.widgets += [self.ent]
        btn = DirectButton(text=_('Connect'), pos=(0, 1, -.2),
                           command=self.connect, **menu_gui.btn_args)
        self.widgets += [btn]
        PageGui.build_page(self)

    def connect(self):
        try:
            eng.log_mgr.log(self.ent.get())
            eng.client.start(self.mdt.event.process_msg, self.ent.get())
            menu_gui = self.menu.gui
            txt = OnscreenText(
                text=_('Waiting for the server'), scale=.12, pos=(0, -.5),
                font=menu_gui.font, fg=menu_gui.text_fg)
            self.widgets += [txt]
        except ClientError:
            txt = OnscreenText(_('Error'), fg=(1, 0, 0, 1), scale=.5)
            args = (5.0, lambda tsk: txt.destroy(), 'destroy error text')
            taskMgr.doMethodLater(*args)


class ClientPage(Page):
    gui_cls = ClientPageGui
    event_cls = ClientEvent

    @property
    def init_lst(self):
        return [
            [(self.build_fsm, 'Fsm')],
            [(self.build_gfx, 'Gfx')],
            [(self.build_phys, 'Phys')],
            [(self.build_gui, 'ClientPageGui', [self.menu])],
            [(self.build_logic, 'Logic')],
            [(self.build_audio, 'Audio')],
            [(self.build_ai, 'Ai')],
            [(self.build_event, 'ClientEvent')]]
