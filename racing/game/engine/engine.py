from sys import path

from os.path import dirname, realpath
path.append(dirname(realpath(__file__)) + '/../thirdparty')

import __builtin__
from direct.showbase.ShowBase import ShowBase
from .pause import PauseMgr
from .font import FontMgr
from .log import LogMgr
from .lang import LangMgr
from .gfx import EngineGfx
from .gui.gui import EngineGui
from .phys import EnginePhys
from .logic import EngineLogic
from .event import EngineEvent
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
        self.conf = conf
        GameObjectMdt.__init__(self)

    @property
    def init_lst(self):
        return [
            [(self.build_fsm, 'Fsm')],
            [(self.build_logic, 'EngineLogic', [self.conf])],
            [(self.build_log_mgr, 'LogMgr')],
            [(self.build_lang_mgr, 'LangMgr')],
            [(self.build_gfx, 'EngineGfx')],
            [(self.build_phys, 'EnginePhys')],
            [(self.build_gui, 'EngineGui')],
            [(self.build_audio, 'EngineAudio')],
            [(self.build_ai, 'Ai')],
            [(self.build_event, 'EngineEvent')],
            [(self.build_pause, 'PauseMgr')],
            [(self.build_font_mgr, 'FontMgr')],
            [(self.build_server, 'Server')],
            [(self.build_client, 'Client')]]

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
