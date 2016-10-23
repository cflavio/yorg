from direct.gui.DirectButton import DirectButton
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectEntry
from racing.game.engine.gui.page import Page, PageGui
from racing.game.engine.network.client import ClientError
from .carpage import CarPage
from .netmsgs import NetMsgs


class ClientPageGui(PageGui):

    def __init__(self, mdt, menu):
        self.ent = None
        PageGui.__init__(self, mdt, menu)

    def build(self):
        menu_gui = self.menu.gui
        menu_args = self.menu.gui.menu_args
        txt = OnscreenText(text='', scale=.12, pos=(0, .4),
                           font=menu_gui.font, fg=(.75, .75, .75, 1))
        self.widgets += [txt]
        PageGui.transl_text(self.widgets[0], _('Client'))
        self.ent = DirectEntry(
            scale=.12, pos=(-.68, 1, .2), entryFont=menu_gui.font, width=12,
            frameColor=menu_args.btn_color,
            initialText='insert the server address')
        self.ent.onscreenText['fg'] = (.75, .75, .75, 1)
        self.widgets += [self.ent]
        btn = DirectButton(
            text=_('Connect'), scale=.2, pos=(0, 1, -.2),
            text_fg=(.75, .75, .75, 1),
            text_font=menu_gui.font, frameColor=menu_args.btn_color,
            command=self.connect, frameSize=menu_args.btn_size,
            rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
            clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))
        self.widgets += [btn]
        PageGui.build(self)

    def connect(self):
        try:
            print self.ent.get()
            eng.client.start(self.process_msg, self.ent.get())
            menu_gui = self.menu.gui
            txt = OnscreenText(
                text=_('Waiting for the server'), scale=.12, pos=(0, -.5),
                font=menu_gui.font, fg=(.75, .75, .75, 1))
            self.widgets += [txt]
        except ClientError:
            txt = OnscreenText(_('Error'), fg=(1, 0, 0, 1), scale=.5)
            args = (5.0, lambda tsk: txt.destroy(), 'destroy error text')
            taskMgr.doMethodLater(*args)

    def process_msg(self, data_lst, sender):
        if data_lst[0] == NetMsgs.track_selected:
            eng.log_mgr.log('track selected: ' + data_lst[1])
            self.menu.track = data_lst[1]
            self.menu.logic.push_page(CarPage(self.menu))


class ClientPage(Page):
    gui_cls = ClientPageGui
