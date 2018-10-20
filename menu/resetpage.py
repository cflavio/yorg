from socket import socket, gethostbyname, gaierror, SHUT_RDWR, create_connection, timeout
from hashlib import sha512
from panda3d.core import TextNode
from yyagl.lib.gui import Btn, CheckBtn, Entry, Text
from yyagl.engine.gui.page import Page, PageFacade
from yyagl.gameobject import GameObject
from .thankspage import ThanksPageGui
from .reset_dlg import ResetDialog


class ResetPageGui(ThanksPageGui):

    def __init__(self, mediator, mp_props):
        self.props = mp_props
        ThanksPageGui.__init__(self, mediator, mp_props.gameprops.menu_args)

    def build(self):
        menu_args = self.menu_args
        t_a = menu_args.text_args.copy()
        # del t_a['scale']
        email_lab = Text(_('Your email:'), pos=(-.25, .4),
                               align='right', **t_a)
        jid_lab = Text(_('Your user id:'), pos=(-.25, .2),
                               align='right', **t_a)
        init_txt = self.props.opt_file['settings']['login']['usr'] if \
            self.props.opt_file['settings']['login']['usr'] else \
            _('your user id')
        self.email_ent = Entry(
            scale=.08, pos=(-.15, 1, .4), entryFont=menu_args.font, width=12,
            frameColor=menu_args.btn_color, initialText=_('your email'),
            text_fg=menu_args.text_active, on_tab=self.on_tab_email,
            on_click=self.on_click_email)
        self.jid_ent = Entry(
            scale=.08, pos=(-.15, 1, .2), entryFont=menu_args.font, width=12,
            frameColor=menu_args.btn_color, initialText=init_txt,
            text_fg=menu_args.text_active, on_tab=self.on_tab_id,
            on_click=self.on_click_id)
        start_btn = Btn(
            text=_('Reset'), pos=(-.2, 1, -.2), command=self.reset,
            **self.props.gameprops.menu_args.btn_args)
        t_a['scale'] = .06
        widgets = [self.jid_ent, start_btn, jid_lab, email_lab, self.email_ent]
        self.add_widgets(widgets)
        self.eng.attach_obs(self.on_frame)
        ThanksPageGui.build(self)

    def reset(self, pwd_name=None):
        def process_msg(data_lst, sender):
            print sender, data_lst
        self.eng.client.start(process_msg, self.eng.cfg.dev_cfg.server)
        self.eng.client.register_rpc('reset')
        self.ret_val = ret_val = self.eng.client.reset(self.jid_ent.get(), self.email_ent.get())
        ok_txt = _(
            "We've sent an email to you (please check your spam folder if you "
            "can't find it) with the instructions for completing the reset.")
        nomail_txt = _("This email isn't in our archive.")
        nonick_txt = _("This nickname isn't in our archive.")
        dontmatch_txt = _("This nickname-email pair isn't in our archive.")
        err_txt = _('Connection error.')
        if ret_val == 'ok': txt = ok_txt
        elif ret_val == 'nomail': txt = nomail_txt
        elif ret_val == 'nonick': txt = nonick_txt
        elif ret_val == 'dontmatch': txt = dontmatch_txt
        else: txt = err_txt
        self.reset_dlg = ResetDialog(self.menu_args, txt)
        self.reset_dlg.attach(self.on_reset_dlg)

    def on_reset_dlg(self):
        self.reset_dlg.destroy()
        if self.ret_val == 'ok':
            self._on_back()

    def on_frame(self):
        init_txt = _('your user id')
        curr_txt = self.jid_ent.get()
        if curr_txt == init_txt[:-1]:
            self.jid_ent.set('')
        elif curr_txt.startswith(init_txt) and len(curr_txt) == len(init_txt) + 1:
            self.jid_ent.set(curr_txt[-1:])
        init_txt = _('your email')
        curr_txt = self.email_ent.get()
        if curr_txt == init_txt[:-1]:
            self.email_ent.set('')
        elif curr_txt.startswith(init_txt) and len(curr_txt) == len(init_txt) + 1:
            self.email_ent.set(curr_txt[-1:])

    def on_click_email(self, pos):
        init_txt = _('your email')
        curr_txt = self.email_ent.get()
        if curr_txt == init_txt: self.email_ent.set('')

    def on_click_id(self, pos):
        init_txt = _('your user id')
        curr_txt = self.jid_ent.get()
        if curr_txt == init_txt: self.jid_ent.set('')

    def on_tab_email(self):
        self.email_ent['focus'] = 0
        self.jid_ent['focus'] = 1

    def on_tab_id(self):
        self.email_ent['focus'] = 0
        self.jid_ent['focus'] = 0

    def on_ok(self):
        self.props.opt_file['settings']['login']['usr'] = self.jid_ent.get()
        if self.store_cb['indicatorValue']:
            self.props.opt_file['settings']['login']['pwd'] = self.pwd_ent.get()
        self.props.opt_file.store()
        self._on_back()
        self.notify('on_login')

    def on_ko(self, err):  # unused err
        txt = Text(_('Error'), pos=(-.2, -.05), fg=(1, 0, 0, 1),
                           scale=.16, font=self.menu_args.font)
        self.eng.do_later(5, txt.destroy)

    def destroy(self):
        self.eng.detach_obs(self.on_frame)
        ThanksPageGui.destroy(self)


class ResetPage(Page):
    gui_cls = ResetPageGui

    def __init__(self, mp_props):
        init_lst = [
            [('event', self.event_cls, [self])],
            [('gui', self.gui_cls, [self, mp_props])]]
        GameObject.__init__(self, init_lst)
        PageFacade.__init__(self)
        # invoke Page's __init__

    def destroy(self):
        GameObject.destroy(self)
        PageFacade.destroy(self)
