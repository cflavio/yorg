from itertools import chain
from yyagl.lib.gui import Btn, Label, Frame
from direct.gui.DirectLabel import DirectLabel
from panda3d.core import TextNode
from yyagl.gameobject import GameObject
from .forms import UserFrm, UserFrmMe, UserFrmMatch


class MatchFrm(GameObject):

    def __init__(self, menu_props, room):
        GameObject.__init__(self)
        self.eng.log('created match form (init)')
        self.room = room
        self.invited_users = [self.eng.client.myid]
        self.menu_props = menu_props
        lab_args = menu_props.label_args
        lab_args['scale'] = .046
        self.match_frm = Frame(
            frame_size=(-.02, 3.49, 0, .45),
            frame_col=(.2, .2, .2, .5),
            pos=(.04, -.46), parent=base.a2dTopLeft)
        usr = [usr for usr in self.eng.client.users if usr.uid == self.eng.client.myid][0]
        frm = UserFrmMe(
            self.eng.client.myid, usr.is_supporter, (.1, .38), self.match_frm,
            self.menu_props, .32)
        self.forms = [frm]
        for i in range(0, 8):
            row, col = i % 4, i // 4
            Label(
                text=str(i + 1) + '.', pos=(.06 + 1.24 * col, .38 - .08 * row),
                parent=self.match_frm, **lab_args)

    @property
    def widgets(self):
        return [self.match_frm] + list(chain(*[frm.widgets for frm in self.forms]))

    def on_presence_available_room(self, uid, room):
        #room = str(JID(msg['muc']['room']).bare)
        #nick = str(msg['muc']['nick'])
        self.eng.log('user %s has connected to the room %s' % (uid, room))
        if uid == self.eng.client.myid: return
        if room != self.room: return
        found = False
        for frm in self.forms:
            lab = frm.lab.lab['text']
            lab = lab.replace('\1smaller\1', '').replace('\2', '')
            if lab.startswith('? '): lab = lab[2:]
            if lab == uid:
                found = True
                frm.lab.lab['text'] = frm.lab.lab['text'][2:]
        if not found:
            idx = len(self.forms)
            x = .1 + 1.24 * (idx / 4)
            y = .38 - .08 * (idx % 4)
            usr = [usr for usr in self.eng.client.users if usr.uid == uid][0]
            frm = UserFrm(uid, usr.is_supporter,
                          (x, y), self.match_frm, self.menu_props, 1.0)
            self.forms += [frm]

    def on_presence_unavailable_room(self, uid, room_name):
        room = room_name
        nick = uid
        self.eng.log('user %s has disconnected from the room %s' % (nick, room))
        if room != self.room: return
        for i, frm in enumerate(self.forms[:]):
            lab = frm.lab.lab['text']
            lab = lab.replace('\1smaller\1', '').replace('\2', '')
            if lab == nick:
                for j in range(i + 1, 8):
                    if j < len(self.forms):
                        self.set_frm_pos(self.forms[j], j - 1)
                self.forms.remove(frm)
                frm.destroy()

    def on_rm_usr_from_match(self, data_lst):
        nick = data_lst[0]
        room = data_lst[1]
        self.eng.log('user %s has been removed from the room %s' % (nick, room))
        if room != self.room: return
        for i, frm in enumerate(self.forms[:]):
            lab = frm.lab.lab['text']
            lab = lab.replace('\1smaller\1', '').replace('\2', '')
            if nick == lab or '? ' + nick == lab:
                for j in range(i + 1, 8):
                    if j < len(self.forms):
                        self.set_frm_pos(self.forms[j], j - 1)
                self.forms.remove(frm)
                frm.destroy()

    @property
    def users_names(self):
        clean = lambda lab: lab.replace('\1smaller\1', '').replace('\2', '')
        return [clean(frm.lab.lab['text']) for frm in self.forms]

    def set_frm_pos(self, frm, i):
        row, col = i % 4, i / 4
        x = .1 + 1.24 * col
        y = .38 - .08 * row
        frm.frm.set_pos((x, 1, y))

    def on_declined(self, from_):
        self.eng.log('user %s has declined' % from_)
        for i, frm in enumerate(self.forms[:]):
            lab = frm.lab.lab['text']
            lab = lab.replace('\1smaller\1', '').replace('\2', '')
            if lab.startswith('? '): lab = lab[2:]
            if lab == from_:
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
        self.eng.log('match form: invited user ' + usr.uid)
        idx = len(self.invited_users)
        x = .1 + 1.24 * (idx / 4)
        y = .38 - .08 * (idx % 4)
        frm = UserFrmMatch('? ' + self.trunc(usr.uid, 30), usr, usr.is_supporter, (x, 1, y),
                           self.match_frm, self.menu_props)
        frm.attach(self.on_remove)
        self.forms += [frm]
        self.invited_users += [usr.uid]

    def on_start(self):
        self.eng.log('match form: start')
        self.notify('on_start')

    def on_remove(self, usr_name):
        self.eng.client.register_rpc('rm_usr_from_match')
        self.eng.client.rm_usr_from_match(usr_name, self.room)

    def show(self, room):
        self.eng.log('match form: show room ' + room)
        self.room = room
        self.match_frm.show()

    def hide(self):
        self.eng.log('match form: hide')
        self.match_frm.hide()

    def destroy(self):
        self.eng.log('match form: destroy')
        self.match_frm.destroy()
        GameObject.destroy(self)


class MatchFrmServer(MatchFrm):

    def __init__(self, menu_props, room):
        MatchFrm.__init__(self, menu_props, room)
        btn_args = self.menu_props.btn_args
        btn_args['scale'] = (.06, .06)
        self.start_btn = Btn(
            text=_('Start'), pos=(1.68, .03), cmd=self.on_start,
            parent=self.match_frm, **btn_args)

    @property
    def widgets(self): return [self.start_btn] + MatchFrm.widgets.fget(self)


class MatchFrmServerClient(MatchFrm):

    def __init__(self, menu_props, room):
        MatchFrm.__init__(self, menu_props, room)
        lab_args = menu_props.label_args
        lab_args['scale'] = .046
        self.client_lab = Label(
            text=_('please wait for the server'), pos=(1.68, .03),
            parent=self.match_frm, text_wordwrap=36, **lab_args)

    @property
    def widgets(self): return [self.client_lab] + MatchFrm.widgets.fget(self)
