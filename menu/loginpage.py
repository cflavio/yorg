from socket import socket, gethostbyname, gaierror, SHUT_RDWR, create_connection, timeout
from hashlib import sha512
from panda3d.core import TextNode
from yyagl.lib.gui import Btn, CheckBtn, Entry, Text
from yyagl.engine.gui.page import Page
from yyagl.gameobject import GameObject
from .thankspage import ThanksPageGui


class LogInPageGui(ThanksPageGui):

    def __init__(self, mediator, mp_props):
        self.props = mp_props
        ThanksPageGui.__init__(self, mediator, mp_props.gameprops.menu_props)

    def build(self):
        menu_props = self.menu_props
        t_a = menu_props.text_args.copy()
        # del t_a['scale']
        jid_lab = Text(_('Your user id:'), pos=(-.05, .4),
                               align='right', **t_a)
        pwd_lab = Text(_('Your password:'), pos=(-.05, .2),
                               align='right', **t_a)
        init_txt = self.props.opt_file['settings']['login']['usr'] if \
            self.props.opt_file['settings']['login']['usr'] else \
            _('your user id')
        self.jid_ent = Entry(
            scale=.08, pos=(.05, .4), entry_font=menu_props.font, width=12,
            frame_col=menu_props.btn_col, initial_text=init_txt,
            text_fg=menu_props.text_active_col, on_tab=self.on_tab,
            on_click=self.on_click)
        self.pwd_ent = Entry(
            scale=.08, pos=(.05, .2), entry_font=menu_props.font, width=12,
            frame_col=menu_props.btn_col, obscured=True,
            text_fg=menu_props.text_active_col, cmd=self.start)
        start_btn = Btn(
            text=_('Log-in'), pos=(0, 0), cmd=self.start,
            **self.props.gameprops.menu_props.btn_args)
        widgets = [self.jid_ent, self.pwd_ent, start_btn, jid_lab,
                   pwd_lab]
        self.add_widgets(widgets)
        self.eng.attach_obs(self.on_frame)
        ThanksPageGui.build(self)

    def start(self, pwd_name=None):
        def process_msg(data_lst, sender):
            print(sender, data_lst)
        #self.eng.client.start(process_msg, self.eng.cfg.dev_cfg.server)
        self.eng.client.register_rpc('login')
        self.eng.client.register_rpc('get_salt')
        #self.eng.client.restart()
        salt = self.eng.client.get_salt(self.jid_ent.text)
        self.pwd = sha512(self.pwd_ent.text.encode() + salt.encode()).hexdigest()
        ret_val = self.eng.client.login(self.jid_ent.text, self.pwd)
        if ret_val in ['invalid_nick', 'unregistered_nick', 'wrong_pwd', 'unactivated']:
            return self.on_ko(ret_val)
        self.on_ok()

    def on_frame(self):
        init_txt = _('your user id')
        curr_txt = self.jid_ent.text
        if curr_txt == init_txt[:-1]:
            self.jid_ent.set('')
        elif curr_txt.startswith(init_txt) and len(curr_txt) == len(init_txt) + 1:
            self.jid_ent.set(curr_txt[-1:])

    def on_click(self, pos):
        init_txt = _('your user id')
        curr_txt = self.jid_ent.text
        if curr_txt == init_txt: self.jid_ent.set('')

    def on_tab(self):
        self.jid_ent['focus'] = 0
        self.pwd_ent['focus'] = 1

    def on_ok(self):
        self.eng.client.authenticated = True
        self.props.opt_file['settings']['login']['usr'] = self.jid_ent.text
        self.props.opt_file['settings']['login']['pwd'] = self.pwd
        self.props.opt_file.store()
        self.eng.client.init(self.props.opt_file['settings']['login']['usr'])
        self._on_back()
        self.notify('on_login_page')

    def on_ko(self, err):
        txt = Text(_('Error') + ': ' + err, pos=(-.2, -.05), fg=(1, 0, 0, 1),
                           scale=.16, font=self.menu_props.font)
        self.eng.do_later(5, txt.destroy)

    def destroy(self):
        self.eng.detach_obs(self.on_frame)
        ThanksPageGui.destroy(self)


class LogInPage(Page):
    gui_cls = LogInPageGui

    def __init__(self, mp_props):
        self.mp_props = mp_props
        Page.__init__(self, mp_props)

    def _build_gui(self):
        self.gui = self.gui_cls(self, self.mp_props)
