from abc import ABCMeta
from direct.fsm.FSM import FSM
from direct.showbase.DirectObject import DirectObject
from .observer import Subject


class Colleague(Subject):

    def __init__(self, mdt):
        Subject.__init__(self)
        self.mdt = mdt

    def destroy(self):
        self.mdt = None
        Subject.destroy(self)


class Fsm(FSM, Colleague):
    def __init__(self, mdt):
        FSM.__init__(self, self.__class__.__name__)
        Colleague.__init__(self, mdt)

    def destroy(self):
        if self.state:
            self.cleanup()
        Colleague.destroy(self)


class Event(Colleague, DirectObject):

    def destroy(self):
        Colleague.destroy(self)
        self.ignoreAll()


class Audio(Colleague):
    pass


class Ai(Colleague):
    pass


class Gfx(Colleague):
    pass


class Gui(Colleague):
    pass


class Logic(Colleague):
    pass


class Phys(Colleague):
    pass


class GameObjectMdt(object):
    __metaclass__ = ABCMeta
    gfx_cls = Gfx
    gui_cls = Gui
    logic_cls = Logic
    audio_cls = Audio
    phys_cls = Phys
    ai_cls = Ai
    event_cls = Event
    fsm_cls = Fsm

    def __init__(self):
        self.fsm = self.fsm_cls(self)
        self.gfx = self.gfx_cls(self)
        self.phys = self.phys_cls(self)
        self.gui = self.gui_cls(self)
        self.logic = self.logic_cls(self)
        self.audio = self.audio_cls(self)
        self.ai = self.ai_cls(self)
        self.event = self.event_cls(self)

    def destroy(self):
        self.fsm.destroy()
        self.phys.destroy()
        self.gfx.destroy()
        self.gui.destroy()
        self.logic.destroy()
        self.audio.destroy()
        self.ai.destroy()
        self.event.destroy()
