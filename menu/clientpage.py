from panda3d.core import TextNode
from direct.gui.DirectScrolledFrame import DirectScrolledFrame
from direct.gui.DirectGuiGlobals import FLAT
from yyagl.lib.gui import Btn, Label
from yyagl.engine.gui.page import Page, PageFacade
from yyagl.gameobject import GameObject
from .thankspage import ThanksPageGui
from multiplayer.forms import UserFrmList


class ClientPageGui(ThanksPageGui):

    def __init__(self, mediator, menu_props):
        self.menu_props = menu_props
        ThanksPageGui.__init__(self, mediator, menu_props.gameprops.menu_props)

    def show(self):
        ThanksPageGui.show(self)
        self.build()

    def build(self):
        widgets = []
        self.add_widgets(widgets)
        ThanksPageGui.build(self)
        lab_args = self.menu_props.label_args
        lab_args['scale'] = .046
        self.users_lab = Label(
            text=_('Current waiting hosting users'), pos=(.02, -.05),
            parent=base.a2dTopLeft, text_wordwrap=48,
            text_align=TextNode.A_left, **lab_args)
        self.frm = DirectScrolledFrame(
            frameSize=(-.02, 2.6, .7, 2.43),
            canvasSize=(-.02, 2.56, -.08, 3.8),
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
            frameColor=(.2, .2, .2, .5),
            pos=(.04, 1, -2.5), parent=base.a2dTopLeft)
        self.labels = []
        self.invited_users = []
        self.on_hosting()

    @staticmethod
    def trunc(name, lgt):
        if len(name) > lgt: return name[:lgt] + '...'
        return name

    def on_hosting(self):
        bare_users = [self.trunc(user.uid, 20)
                      for user in self.eng.client.sorted_users]
        for lab in self.labels[:]:
            _lab = lab.lab.lab['text'].replace('\1smaller\1', '').replace('\2', '')
            if _lab not in bare_users:
                if _lab not in self.eng.client.users:
                    lab.destroy()
                    self.labels.remove(lab)
        nusers = len(self.eng.client.sorted_users)
        top = .08 * nusers + .08
        self.frm['canvasSize'] = (-.02, .76, 0, top)
        label_users = [lab.lab.lab['text'] for lab in self.labels]
        clean = lambda n: n.replace('\1smaller\1', '').replace('\2', '')
        label_users = map(clean, label_users)

        self.eng.client.register_rpc('hosting')
        hosting = self.eng.client.hosting()
        self.eng.log('hosting %s' % hosting)

        for i, hst in enumerate(hosting):
            if self.trunc(hst, 20) not in label_users:
                if self.eng.client.myid != hst:
                    lab = UserFrmList(
                        hst, 0, 0, (0, top - .08 - .08 * i),
                        self.frm.getCanvas(), self.menu_props)
                    self.labels += [lab]
                    lab.attach(self.on_clicked)

    def on_clicked(self, roomname):
        #self.eng.log('join to the room ' + roomname)
        #self.eng.client.register_rpc('join_room')
        #self.eng.client.join_room(roomname)
        self.eng.client.is_client_active = True
        nick = self.eng.client.myid
        self.notify('on_create_room_client', roomname, nick)

    def destroy(self):
        self.frm.destroy()
        self.users_lab.destroy()


class ClientPage(Page):
    gui_cls = ClientPageGui

    def __init__(self, menu_props):
        self.menu_props = menu_props
        Page.__init__(self, menu_props)
        PageFacade.__init__(self)

    @property
    def init_lst(self): return [
        [('event', self.event_cls, [self])],
        [('gui', self.gui_cls, [self, self.menu_props])]]

    def destroy(self):
        Page.destroy(self)
        PageFacade.destroy(self)
