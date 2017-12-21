from panda3d.core import TextNode
from direct.gui.DirectCheckButton import DirectCheckButton
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectEntry import DirectEntry
from direct.gui.OnscreenText import OnscreenText
from yyagl.engine.gui.page import Page, PageFacade
from yyagl.gameobject import GameObject
from .thankspage import ThanksPageGui


class LogInPageGui(ThanksPageGui):

    def __init__(self, mdt, mp_props):
        self.props = mp_props
        ThanksPageGui.__init__(self, mdt, mp_props.gameprops.menu_args)

    def bld_page(self):
        menu_args = self.menu_args
        t_a = menu_args.text_args.copy()
        #del t_a['scale']
        jid_lab = OnscreenText(_('Your jabber id:'), pos=(-.05, .6),
                               align=TextNode.A_right, **t_a)
        pwd_lab = OnscreenText(_('Your jabber password:'), pos=(-.05, .4),
                               align=TextNode.A_right, **t_a)
        self.jid_ent = DirectEntry(
            scale=.08, pos=(.05, 1, .6), entryFont=menu_args.font, width=12,
            frameColor=menu_args.btn_color, initialText=_('your jabber id'))
        self.pwd_ent = DirectEntry(
            scale=.08, pos=(.05, 1, .4), entryFont=menu_args.font, width=12,
            frameColor=menu_args.btn_color, obscured=True)
        self.jid_ent.onscreenText['fg'] = menu_args.text_fg
        self.pwd_ent.onscreenText['fg'] = menu_args.text_fg
        start_btn = DirectButton(
            text=_('Log-in'), pos=(0, 1, .2), command=self.start,
            **self.props.gameprops.menu_args.btn_args)
        self.store_cb = DirectCheckButton(
            pos=(0, 1, -.2), text=_('store the password'),
            indicatorValue=False, indicator_frameColor=menu_args.text_fg,
            **menu_args.checkbtn_args)
        store_lab = OnscreenText(
        _('(only if your computer is not shared with other people)'), pos=(0, -.4), **t_a)
        widgets = [self.jid_ent, self.pwd_ent, start_btn, jid_lab, pwd_lab,
                   self.store_cb, store_lab]
        map(self.add_widget, widgets)
        ThanksPageGui.bld_page(self)

    def start(self):
        connected = self.eng.xmpp.start(self.jid_ent.get(), self.pwd_ent.get(),
                                        self.on_ok, self.on_ko)

    def on_ok(self):
        if self.store_cb['indicatorValue']:
            self.props.opt_file['settings']['xmpp']['usr'] = self.jid_ent.get()
            self.props.opt_file['settings']['xmpp']['pwd'] = self.pwd_ent.get()
            self.props.opt_file.store()
        self._on_back()
        self.notify('on_login')

    def on_ko(self, err):
        txt = OnscreenText(_('Error'), pos=(0, -.05), fg=(1, 0, 0, 1),
                           scale=.16, font=self.menu_args.font)
        self.eng.do_later(5, txt.destroy)


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
