from abc import ABCMeta
from direct.fsm.FSM import FSM
from direct.showbase.DirectObject import DirectObject
from .observer import Subject


class Colleague(Subject):

    def __init__(self, mdt, *args, **kwargs):
        Subject.__init__(self)
        self.mdt = mdt
        self._args = args
        self._kwargs = kwargs
        self.async_build(*args, **kwargs)

    def async_build(self, *args, **kwargs):
        self._end_async()

    def _end_async(self):
        self.sync_build(*self._args, **self._kwargs)
        taskMgr.doMethodLater(.001, self.__notify, 'wait')

    def __notify(self, task):
        self.mdt.notify('on_component_built', self)

    def sync_build(self, *args, **kwargs):
        pass

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


class GODirector(object):

    def __init__(self, obj, init_lst, cb):
        obj.attach(self.on_component_built)
        self.cb = cb
        self.completion = {}
        for i in range(len(init_lst)):
            self.completion[i] = False
        self.pending = {}
        self.__init_lst = init_lst
        for idx in range(len(init_lst)):
            self.__process_lst(obj, idx)

    def __process_lst(self, obj, idx):
        if not self.__init_lst[idx]:
            self.end_lst(idx)
            return
        comp_info = self.__init_lst[idx].pop(0)
        self.pending[comp_info[1].__name__] = idx
        args = comp_info[2] if len(comp_info) > 2 else []
        setattr(obj, comp_info[0], comp_info[1](*args))
        if len(comp_info) > 3:
            comp_info[3]()

    def on_component_built(self, obj):
        self.__process_lst(obj.mdt, self.pending[obj.__class__.__name__])

    def end_lst(self, idx):
        self.completion[idx] = True
        if all(self.completion[i] for i in self.completion) and self.cb:
            self.cb()


class GameObjectMdt(Subject):
    __metaclass__ = ABCMeta
    gfx_cls = Gfx
    gui_cls = Gui
    logic_cls = Logic
    audio_cls = Audio
    phys_cls = Phys
    ai_cls = Ai
    event_cls = Event
    fsm_cls = Fsm

    def __init__(self, init_lst=[], cb=None):
        Subject.__init__(self)
        init_lst = init_lst or [
            [('fsm', self.fsm_cls, [self])],
            [('gfx', self.gfx_cls, [self])],
            [('phys', self.phys_cls, [self])],
            [('gui', self.gui_cls, [self])],
            [('logic', self.logic_cls, [self])],
            [('audio', self.audio_cls, [self])],
            [('ai', self.ai_cls, [self])],
            [('event', self.event_cls, [self])]]
        GODirector(self, init_lst, cb)

    def build_fsm(self):
        self.fsm = self.fsm_cls(self)

    def build_gfx(self):
        self.gfx = self.gfx_cls(self)

    def build_phys(self):
        self.phys = self.phys_cls(self)

    def build_gui(self):
        self.gui = self.gui_cls(self)

    def build_logic(self):
        self.logic = self.logic_cls(self)

    def build_audio(self):
        self.audio = self.audio_cls(self)

    def build_ai(self):
        self.ai = self.ai_cls(self)

    def build_event(self):
        self.event = self.event_cls(self)

    def __safe_destroy(self, component):
        if hasattr(self, component):
            getattr(self, component).destroy()

    def destroy(self):
        comps = ['fsm', 'phys', 'gfx', 'gui', 'logic', 'audio', 'ai', 'event']
        map(self.__safe_destroy, comps)
