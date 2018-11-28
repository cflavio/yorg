from socket import socket, gethostbyname, gaierror, SHUT_RDWR, create_connection, timeout
from hashlib import sha512
from panda3d.core import TextNode
from yyagl.lib.gui import Btn, CheckBtn, Entry, Text
from yyagl.engine.gui.page import Page, PageFacade
from yyagl.gameobject import GameObject
from .thankspage import ThanksPageGui
from .register_dlg import RegisterDialog


class RegisterPageGui(ThanksPageGui):

    def __init__(self, mediator, mp_props):
        self.props = mp_props
        ThanksPageGui.__init__(self, mediator, mp_props.gameprops.menu_props)

    def build(self):
        menu_props = self.menu_props
        t_a = menu_props.text_args.copy()
        # del t_a['scale']
        email_lab = Text(_('Your email:'), pos=(-.85, .4),
                               align='right', **t_a)
        jid_lab = Text(_('Your user id:'), pos=(-.85, .2),
                               align='right', **t_a)
        pwd_lab = Text(_('Your password:'), pos=(-.85, .0),
                               align='right', **t_a)
        init_txt = self.props.opt_file['settings']['login']['usr'] if \
            self.props.opt_file['settings']['login']['usr'] else \
            _('your user id')
        self.email_ent = Entry(
            scale=.08, pos=(-.75, .4), entry_font=menu_props.font, width=20,
            frame_col=menu_props.btn_col, initial_text=_('your email'),
            text_fg=menu_props.text_active_col, on_tab=self.on_tab_email,
            on_click=self.on_click_email)
        self.jid_ent = Entry(
            scale=.08, pos=(-.75, .2), entry_font=menu_props.font, width=20,
            frame_col=menu_props.btn_col, initial_text=init_txt,
            text_fg=menu_props.text_active_col, on_tab=self.on_tab_id,
            on_click=self.on_click_id)
        self.pwd_ent = Entry(
            scale=.08, pos=(-.75, 0), entry_font=menu_props.font, width=20,
            frame_col=menu_props.btn_col, obscured=True,
            text_fg=menu_props.text_active_col, cmd=self.register)
        start_btn = Btn(
            text=_('Register'), pos=(-.2, -.2), cmd=self.register,
            **self.props.gameprops.menu_props.btn_args)
        t_a['scale'] = .06
        widgets = [self.jid_ent, self.pwd_ent, start_btn, jid_lab, pwd_lab,
                   email_lab, self.email_ent]
        self.add_widgets(widgets)
        self.eng.attach_obs(self.on_frame)
        ThanksPageGui.build(self)

    def register(self, pwd_name=None):
        def process_msg(data_lst, sender):
            print sender, data_lst
        if len(self.pwd_ent.text) >= 6:
            self.eng.client.start(process_msg)
            self.eng.client.register_rpc('register')
            self.eng.client.register_rpc('get_salt')
            salt = self.eng.client.get_salt(self.jid_ent.text)
            ret_val = self.eng.client.register(
                self.jid_ent.text,
                sha512(self.pwd_ent.text + salt).hexdigest(), salt,
                self.email_ent.text.replace('_AT_', '@'))
        else: ret_val = 'short'
        self.ret_val = ret_val
        ok_txt = _(
            'Your account has been registered. Now, in order to '
            "activate it, you should click the link that we've sent to your "
            "email (please check your spam folder if you can't find it). "
            'After that, you can log in.')
        inv_nick_txt = _(
            "Your nickname's format is invalid: please use only letters and "
            'numbers.')
        inv_email_txt = _("Your email's format is invalid.")
        already_nick_txt = _('Your nickname already exists.')
        already_email_txt = _('Your email has already been used.')
        short_txt = _('Please use more than 6 characters for your password.')
        err_txt = _('Connection error.')
        if ret_val == 'ok': txt = ok_txt
        elif ret_val == 'invalid_nick': txt = inv_nick_txt
        elif ret_val == 'invalid_email': txt = inv_email_txt
        elif ret_val == 'already_used_nick': txt = already_nick_txt
        elif ret_val == 'already_used_email': txt = already_email_txt
        elif ret_val == 'short': txt = short_txt
        else: txt = err_txt
        self.register_dlg = RegisterDialog(self.menu_props, txt)
        self.register_dlg.attach(self.on_register_dlg)

    def on_register_dlg(self):
        self.register_dlg.destroy()
        if self.ret_val == 'ok':
            self._on_back()

    def on_frame(self):
        init_txt = _('your user id')
        curr_txt = self.jid_ent.text
        if curr_txt == init_txt[:-1]:
            self.jid_ent.set('')
        elif curr_txt.startswith(init_txt) and len(curr_txt) == len(init_txt) + 1:
            self.jid_ent.set(curr_txt[-1:])
        init_txt = _('your email')
        curr_txt = self.email_ent.text
        if curr_txt == init_txt[:-1]:
            self.email_ent.set('')
        elif curr_txt.startswith(init_txt) and len(curr_txt) == len(init_txt) + 1:
            self.email_ent.set(curr_txt[-1:])

    def on_click_email(self, pos):
        init_txt = _('your email')
        curr_txt = self.email_ent.text
        if curr_txt == init_txt: self.email_ent.set('')

    def on_click_id(self, pos):
        init_txt = _('your user id')
        curr_txt = self.jid_ent.text
        if curr_txt == init_txt: self.jid_ent.set('')

    def on_tab_email(self):
        self.email_ent['focus'] = 0
        self.jid_ent['focus'] = 1
        self.pwd_ent['focus'] = 0

    def on_tab_id(self):
        self.email_ent['focus'] = 0
        self.jid_ent['focus'] = 0
        self.pwd_ent['focus'] = 1

    def on_ok(self):
        self.props.opt_file['settings']['login']['usr'] = self.jid_ent.text
        if self.store_cb['indicatorValue']:
            self.props.opt_file['settings']['login']['pwd'] = self.pwd_ent.text
        self.props.opt_file.store()
        self._on_back()
        self.notify('on_login')

    def on_ko(self, err):  # unused err
        txt = Text(_('Error'), pos=(-.2, -.05), fg=(1, 0, 0, 1),
                           scale=.16, font=self.menu_props.font)
        self.eng.do_later(5, txt.destroy)

    def destroy(self):
        self.eng.detach_obs(self.on_frame)
        ThanksPageGui.destroy(self)


class RegisterPage(Page):
    gui_cls = RegisterPageGui

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
