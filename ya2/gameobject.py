''''In this module we define the GameObject classes.'''
from abc import ABCMeta
from direct.fsm.FSM import FSM
from direct.showbase.DirectObject import DirectObject
from ya2.decorators.evtdec import evt_dec


class Colleague(object):

    def __init__(self, mdt):
        self.mdt = mdt

    def destroy(self):
        pass


class Fsm(FSM, Colleague):
    '''The FSM of the GameObject.'''
    def __init__(self, mdt):
        FSM.__init__(self, self.__class__.__name__)
        Colleague.__init__(self, mdt)


class Event(Colleague, DirectObject):
    '''This class manages the events of the GameObject.'''
    def __init__(self, mdt):
        Colleague.__init__(self, mdt)
        self = evt_dec(self, self.mdt.fsm)


class Audio(Colleague):
    '''This is the audio component of the GameObject.'''
    pass


class Ai(Colleague):
    '''This is the AI component of the GameObject.'''
    pass


class Gfx(Colleague):
    '''This is the graphics component of the GameObject.'''
    pass


class Gui(Colleague):
    '''This is the GUI component of the GameObject.'''
    pass


class Logic(Colleague):
    '''This contains the business logics of the GameObject.'''
    pass


class Phys(Colleague):
    '''This is the physics component of the GameObject.'''
    pass


class GameObjectMdt(object):
    '''This class models the GameObject.'''
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
        self.fsm.cleanup()
        self.fsm.destroy()
        self.phys.destroy()
        self.gfx.destroy()
        self.gui.destroy()
        self.logic.destroy()
        self.audio.destroy()
        self.ai.destroy()
        self.event.destroy()
