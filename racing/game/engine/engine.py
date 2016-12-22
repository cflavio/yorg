from sys import path

from os.path import dirname, realpath
path.append(dirname(realpath(__file__)) + '/../thirdparty')

import __builtin__
from direct.showbase.ShowBase import ShowBase
from .pause import PauseMgr
from .font import FontMgr
from .log import LogMgr
from .lang import LangMgr
from .shader import ShaderMgr
from .gfx import EngineGfx
from .gui.gui import EngineGui, EngineGuiWindow
from .phys import EnginePhys
from .logic import EngineLogic
from .event import EngineEvent, EngineEventWindow
from .audio import EngineAudio
from .network.server import Server
from .network.client import Client
from ..gameobject import GameObjectMdt


class EngineBase(ShowBase):

    pass


class Engine(GameObjectMdt):
    gfx_cls = EngineGfx
    gui_cls = EngineGui
    logic_cls = EngineLogic
    phys_cls = EnginePhys
    event_cls = EngineEvent
    audio_cls = EngineAudio

    def __init__(self, conf=None):
        __builtin__.eng = self
        self.base = EngineBase()
        init_lst = [
            [('fsm', self.fsm_cls, [self])],
            [('logic', EngineLogic, [self, conf])],
            [('log_mgr', LogMgr, [self])],
            [('lang_mgr', LangMgr, [self])],
            [('gfx', EngineGfx, [self])],
            [('phys', EnginePhys, [self])],
            [('gui', self.gui_cls, [self])],
            [('audio', EngineAudio, [self])],
            [('ai', self.ai_cls, [self])],
            [('event', self.event_cls, [self])],
            [('pause', PauseMgr, [self])],
            [('font_mgr', FontMgr, [self])],
            [('server', Server, [self])],
            [('client', Client, [self])],
            [('shader_mgr', ShaderMgr, [self])]]
        GameObjectMdt.__init__(self, init_lst)

    def build_logic(self, conf):
        self.logic = self.logic_cls(self, conf)

    def build_log_mgr(self):
        self.log_mgr = LogMgr(self)
        self.log_mgr.log_conf()

    def build_lang_mgr(self):
        self.lang_mgr = LangMgr(self)

    def build_pause(self):
        self.pause = PauseMgr(self)

    def build_font_mgr(self):
        self.font_mgr = FontMgr(self)

    def build_server(self):
        self.server = Server(self)

    def build_client(self):
        self.client = Client(self)

    def destroy(self):
        GameObjectMdt.destroy(self)
        self.base.destroy()


class EngineWindow(Engine):

    gui_cls = EngineGuiWindow
    event_cls = EngineEventWindow
