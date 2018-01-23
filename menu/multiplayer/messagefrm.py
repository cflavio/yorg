from sleekxmpp.jid import JID
from panda3d.core import TextNode
from direct.gui.DirectGuiGlobals import FLAT, NORMAL, DISABLED
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectScrolledFrame import DirectScrolledFrame
from direct.gui.DirectEntry import DirectEntry
from direct.gui.OnscreenText import OnscreenText
from yyagl.gameobject import GameObject
from yyagl.engine.gui.imgbtn import ImgBtn


class Chat(object):

    def __init__(self, dst, read=True):
        self.dst = dst
        self.messages = []
        self.read = read


class MessageFrm(GameObject):

    def __init__(self, menu_args):
        GameObject.__init__(self)
        self.chats = []
        self.msg_frm = DirectFrame(
            frameSize=(-.02, .8, 0, .45),
            frameColor=(.2, .2, .2, .5),
            pos=(-.82, 1, .02), parent=base.a2dBottomRight)
        self.presences_sent = []
        t_a = menu_args.text_args
        t_a['scale'] = .05
        t_a['fg'] = menu_args.text_normal
        self.dst_txt = OnscreenText(
            text='', pos=(.36, .4), parent=self.msg_frm, **t_a)
        self.left_btn = ImgBtn(
            parent=self.msg_frm, scale=.024, pos=(.02, 1, .42),
            frameColor=(1, 1, 1, 1),
            frameTexture='assets/images/gui/arrow.txo',
            command=self.on_arrow, extraArgs=['left'],
            **menu_args.imgbtn_args)
        self.left_btn.set_r(180)
        self.left_btn.disable()
        self.right_btn = ImgBtn(
            parent=self.msg_frm, scale=.024, pos=(.7, 1, .42),
            frameColor=(1, 1, 1, 1),
            frameTexture='assets/images/gui/arrow.txo',
            command=self.on_arrow, extraArgs=['right'],
            **menu_args.imgbtn_args)
        self.right_btn.disable()
        self.close_btn = ImgBtn(
            parent=self.msg_frm, scale=.024, pos=(.76, 1, .42),
            frameColor=(1, 1, 1, 1),
            frameTexture='assets/images/gui/close.txo',
            command=self.on_close,
            **menu_args.imgbtn_args)
        self.close_btn.disable()
        self.ent = DirectEntry(
            scale=.04, pos=(0, 1, .03), entryFont=menu_args.font, width=19.5,
            frameColor=menu_args.btn_color, parent=self.msg_frm,
            initialText=_('write here your message'),
            command=self.on_typed_msg, focusInCommand=self.on_focus,
            focusInExtraArgs=['in'], focusOutCommand=self.on_focus,
            focusOutExtraArgs=['out'])
        self.ent.onscreenText['fg'] = menu_args.text_active
        self.ent['state'] = DISABLED
        self.txt_frm = DirectScrolledFrame(
            frameSize=(-.02, .76, -.02, .28),
            canvasSize=(-.02, .72, -.02, .28),
            scrollBarWidth=.036,
            verticalScroll_relief=FLAT,
            verticalScroll_frameColor=(.2, .2, .2, .4),
            verticalScroll_thumb_relief=FLAT,
            verticalScroll_thumb_frameColor=(.8, .8, .8, .6),
            verticalScroll_incButton_relief=FLAT,
            verticalScroll_incButton_frameColor=(.8, .8, .8, .6),
            verticalScroll_decButton_relief=FLAT,
            verticalScroll_decButton_frameColor=(.8, .8, .8, .6),
            horizontalScroll_relief=FLAT,
            frameColor=(1, 1, 1, 0),
            pos=(.02, 1, .11), parent=self.msg_frm)
        t_a['scale'] = .046
        self.msg_txt = OnscreenText(
            text='', pos=(0, .24), parent=self.txt_frm.getCanvas(),
            align=TextNode.A_left, wordwrap=14, **t_a)

    def show(self):
        self.msg_frm.show()

    def hide(self):
        self.msg_frm.hide()

    def add_msg_txt(self, msg):
        self.msg_txt['text'] += ('\n' if self.msg_txt['text'] else '') + msg
        txt_height = self.msg_txt.textNode.getUpperLeft3d()[2] - \
            self.msg_txt.textNode.getLowerRight3d()[2]
        self.txt_frm['canvasSize'] = (-.02, .72, .28 - txt_height, .28)

    def set_chat(self, chat):
        self.dst_txt['text'] = chat.dst
        self.msg_txt['text'] = '\n'.join(chat.messages)
        txt_height = self.msg_txt.textNode.getUpperLeft3d()[2] - \
            self.msg_txt.textNode.getLowerRight3d()[2]
        self.txt_frm['canvasSize'] = (-.02, .72, .28 - txt_height, .28)

    def curr_chat(self):
        for chat in self.chats:
            if chat.dst == self.dst_txt['text']:
                return chat

    def on_arrow(self, direction):
        chat_idx = self.chats.index(self.curr_chat())
        step = -1 if direction == 'left' else 1
        next_idx = (chat_idx + step) % len(self.chats)
        chat = self.chats[next_idx]
        self.dst_txt['text'] = chat.dst
        self.set_chat(chat)
        chat.read = True
        if all(_chat.read for _chat in self.chats):
            self.left_btn['frameTexture'] = 'assets/images/gui/arrow.txo'
            self.left_btn.set_r(180)
            self.right_btn['frameTexture'] = 'assets/images/gui/arrow.txo'

    def on_close(self):
        curr_idx = self.chats.index(self.curr_chat())
        self.chats.remove(self.curr_chat())
        if self.chats:
            self.set_chat(self.chats[curr_idx - 1])
            if len(self.chats) == 1:
                self.left_btn.disable()
                self.right_btn.disable()
        else:
            self.set_chat(Chat(''))
            self.close_btn.disable()
            self.ent['state'] = DISABLED

    def on_typed_msg(self, val):
        self.add_msg_txt('\1italic\1' + _('you') + '\2: ' + val)
        self.ent.set('')
        if self.dst_txt['text'] not in self.presences_sent:
            self.eng.xmpp.xmpp.send_presence(
                pfrom=self.eng.xmpp.xmpp.boundjid.full,
                pto=self.dst_txt['text'])
            self.presences_sent += [self.dst_txt['text']]
        self.eng.xmpp.xmpp.send_message(
            mfrom=self.eng.xmpp.xmpp.boundjid.full,
            mto=self.dst_txt['text'],
            mtype='chat',
            msubject='chat',
            mbody=val)
        msg = '\1italic\1' + _('you') + '\2: ' + val
        self.__find_chat(self.dst_txt['text']).messages += [msg]

    def __find_chat(self, usr):
        chats = [chat for chat in self.chats if chat.dst == usr]
        if chats: return chats[0]

    def on_msg(self, msg):
        self.close_btn.enable()
        self.ent['state'] = NORMAL
        str_msg = '\1italic\1' + str(JID(msg['from']).bare) + '\2: ' + str(msg['body'])
        chat = self.__find_chat(str(JID(msg['from']).bare))
        if not chat:
            chat = Chat(str(JID(msg['from']).bare))
            self.chats += [chat]
        chat.messages += [str_msg]
        if self.dst_txt['text'] == '':
            self.set_chat(chat)
        elif self.dst_txt['text'] == str(JID(msg['from']).bare):
            self.add_msg_txt(str_msg)
        else:
            chat.read = False
            self.left_btn['frameTexture'] = 'assets/images/gui/message.txo'
            self.left_btn.enable()
            self.left_btn.set_r(0)
            self.right_btn['frameTexture'] = 'assets/images/gui/message.txo'
            self.right_btn.enable()

    def add_chat(self, usr):
        self.close_btn.enable()
        self.ent['state'] = NORMAL
        self.dst_txt['text'] = usr
        chat = self.__find_chat(self.dst_txt['text'])
        if not chat:
            chat = Chat(usr)
            self.chats += [chat]
        self.set_chat(chat)

    def on_focus(self, val):
        if val and self.ent.get() == _('write here your message'):
            self.ent.set('')
        self.notify('on_msg_focus', val)
