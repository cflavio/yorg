from socket import socket, gethostbyname, gaierror, SHUT_RDWR, create_connection, timeout
from panda3d.core import TextNode
from yyagl.library.gui import Btn, CheckBtn, Entry, Text
from yyagl.engine.gui.page import Page, PageFacade
from yyagl.gameobject import GameObject
from .thankspage import ThanksPageGui
from .check_dlg import CheckDialog


class LogInPageGui(ThanksPageGui):

    def __init__(self, mediator, mp_props):
        self.props = mp_props
        ThanksPageGui.__init__(self, mediator, mp_props.gameprops.menu_args)

    def build(self):
        menu_args = self.menu_args
        t_a = menu_args.text_args.copy()
        # del t_a['scale']
        jid_lab = Text(_('Your user id:'), pos=(-.25, .8),
                               align='right', **t_a)
        pwd_lab = Text(_('Your password:'), pos=(-.25, .6),
                               align='right', **t_a)
        init_txt = self.props.opt_file['settings']['login']['usr'] if \
            self.props.opt_file['settings']['login']['usr'] else \
            _('your user id')
        self.jid_ent = Entry(
            scale=.08, pos=(-.15, 1, .8), entryFont=menu_args.font, width=12,
            frameColor=menu_args.btn_color, initialText=init_txt,
            text_fg=menu_args.text_active, on_tab=self.on_tab,
            on_click=self.on_click)
        self.pwd_ent = Entry(
            scale=.08, pos=(-.15, 1, .6), entryFont=menu_args.font, width=12,
            frameColor=menu_args.btn_color, obscured=True,
            text_fg=menu_args.text_active, command=self.start)
        start_btn = Btn(
            text=_('Log-in'), pos=(-.2, 1, .4), command=self.start,
            **self.props.gameprops.menu_args.btn_args)
        t_a['scale'] = .06
        note_txt = \
            _('If you are a supporter, please write us (%s) your '
              'user id so we can highlight your account as a supporter '
              'one.')
        note_txt = note_txt % 'flavio@ya2.it'
        notes_lab = Text(
            note_txt, pos=(-1.64, .2), align='left', wordwrap=42,
            **t_a)
        register_txt = _(
            "If you don't have an account, then you can register:")
        register_lab = Text(
            register_txt, pos=(-1.64, -.2), align='left', wordwrap=42,
            **t_a)
        register_btn = Btn(
            text='', pos=(-.2, 1, -.35), command=self.on_register,
            tra_src='Register', tra_tra=_('Register'),
            **menu_args.btn_args)
        reset_txt = _(
            "If you want to reset your password:")
        reset_lab = Text(
            reset_txt, pos=(-1.64, -.55), align='left', wordwrap=42,
            **t_a)
        reset_btn = Btn(
            text='', pos=(-.2, 1, -.7), command=self.on_reset,
            tra_src='Reset', tra_tra=_('Reset'),
            **menu_args.btn_args)
        widgets = [self.jid_ent, self.pwd_ent, start_btn, jid_lab, pwd_lab,
                   notes_lab, register_lab, register_btn, reset_lab, reset_btn]
        self.add_widgets(widgets)
        self.eng.attach_obs(self.on_frame)
        ThanksPageGui.build(self)

    def on_register(self):
        self.notify('on_push_page', 'register', [self.props])

    def on_reset(self):
        self.notify('on_push_page', 'reset', [self.props])

    def start(self, pwd_name=None):
        if not self.check(self.jid_ent.get().replace('_AT_', '@')):
            self.check_dlg = CheckDialog(self.menu_args)
            self.check_dlg.attach(self.on_check_dlg)
            return
        self.eng.xmpp.start(self.jid_ent.get().replace('_AT_', '@'),
                            self.pwd_ent.get(), self.on_ok, self.on_ko,
                            self.props.gameprops.xmpp_debug)

    def check(self, jid):
        try:
            jid, domain = jid.split('@')  # check the pattern
            #gethostbyname(domain)  # check if the domain exists
            #s = create_connection((domain, 5222), timeout=3.0)  # xmpp up?
            #s.shutdown(SHUT_RDWR)
            #s.close()
            return True
        except (ValueError, gaierror, timeout) as e:
            print jid, e

    def on_check_dlg(self): self.check_dlg.destroy()

    def on_frame(self):
        init_txt = _('your user id')
        curr_txt = self.jid_ent.get()
        if curr_txt == init_txt[:-1]:
            self.jid_ent.set('')
        elif curr_txt.startswith(init_txt) and len(curr_txt) == len(init_txt) + 1:
            self.jid_ent.set(curr_txt[-1:])

    def on_click(self, pos):
        init_txt = _('your user id')
        curr_txt = self.jid_ent.get()
        if curr_txt == init_txt: self.jid_ent.set('')

    def on_tab(self):
        self.jid_ent['focus'] = 0
        self.pwd_ent['focus'] = 1

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


class LogInPage(Page):
    gui_cls = LogInPageGui

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
