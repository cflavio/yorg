from sleekxmpp.jid import JID
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectLabel import DirectLabel
from panda3d.core import TextNode
from yyagl.gameobject import GameObject
from .forms import UserFrm, UserFrmMe


class MatchFrm(GameObject):

    def __init__(self, menu_args):
        GameObject.__init__(self)
        self.room = ''
        self.invited_users = [self.eng.xmpp.client.boundjid.bare]
        self.menu_args = menu_args
        lab_args = menu_args.label_args
        lab_args['scale'] = .046
        self.match_frm = DirectFrame(
            frameSize=(-.02, 2.5, 0, .45),
            frameColor=(.2, .2, .2, .5),
            pos=(.04, 1, -.46), parent=base.a2dTopLeft)
        btn_args = self.menu_args.btn_args
        btn_args['scale'] = .06
        DirectButton(text=_('Start'), pos=(1.2, 1, .03), command=self.on_start,
                     parent=self.match_frm, **btn_args)
        frm = UserFrmMe(
            self.eng.xmpp.client.boundjid.bare, self.eng.xmpp.client.boundjid.bare,
            False, (.1, 1, .38), self.match_frm, self.menu_args, .32)
        self.forms = [frm]
        for i in range(0, 8):
            row, col = i % 4, i / 4
            DirectLabel(
                text=str(i + 1) + '.', pos=(.06 + 1.24 * col, 1, .38 - .08 * row),
                parent=self.match_frm, **lab_args)

    def on_presence_available_room(self, msg):
        room = str(JID(msg['muc']['room']).bare)
        nick = str(msg['muc']['nick'])
        if nick == self.eng.xmpp.client.boundjid.bare: return
        if room != self.room: return
        found = False
        for frm in self.forms:
            lab = frm.lab['text']
            lab = lab.replace('\1smaller\1', '').replace('\2', '')
            if lab.startswith('? '): lab = lab[2:]
            if lab == nick:
                found = True
                frm.lab['text'] = frm.lab['text'][2:]
        if not found:
            idx = len(self.forms)
            x = .1 + 1.24 * (idx / 4)
            y = .38 - .08 * (idx % 4)
            frm = UserFrm(self.trunc(nick, 30), nick, False, (x, 1, y),
                          self.match_frm, self.menu_args, 1.0)
            self.forms += [frm]

    def on_presence_unavailable_room(self, msg):
        room = str(JID(msg['muc']['room']).bare)
        nick = str(msg['muc']['nick'])
        if room != self.room: return
        for i, frm in enumerate(self.forms[:]):
            lab = frm.lab['text']
            lab = lab.replace('\1smaller\1', '').replace('\2', '')
            if lab == nick:
                for j in range(i + 1, 8):
                    if j < len(self.forms):
                        self.set_frm_pos(self.forms[j], j - 1)
                self.forms.remove(frm)
                frm.destroy()

    def set_frm_pos(self, frm, i):
        row, col = i % 4, i / 4
        x = .1 + 1.24 * col
        y = .38 - .08 * row
        frm.frm.set_pos(x, 1, y)

    def on_declined(self, msg):
        usr = str(JID(msg['from']).bare)
        for i, frm in enumerate(self.forms[:]):
            lab = frm.lab['text']
            lab = lab.replace('\1smaller\1', '').replace('\2', '')
            if lab.startswith('? '): lab = lab[2:]
            if lab == usr:
                for j in range(i + 1, 8):
                    if j < len(self.forms):
                        self.set_frm_pos(self.forms[j], j - 1)
                self.forms.remove(frm)
                frm.destroy()

    @staticmethod
    def trunc(name, lgt):
        if len(name) > lgt: return name[:lgt] + '...'
        return name

    def on_invite(self, usr):
        idx = len(self.invited_users)
        x = .1 + 1.24 * (idx / 4)
        y = .38 - .08 * (idx % 4)
        frm = UserFrm('? ' + self.trunc(usr.name, 30), usr, usr.is_supporter, (x, 1, y),
                      self.match_frm, self.menu_args, 1.0)
        self.forms += [frm]
        self.invited_users += [usr.name]

    def on_start(self):
        self.notify('on_start')

    def show(self, room):
        self.room = room
        self.match_frm.show()

    def hide(self):
        self.match_frm.hide()

    def destroy(self):
        self.match_frm.destroy()
