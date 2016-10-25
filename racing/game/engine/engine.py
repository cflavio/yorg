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
from ..gameobject.gameobject import GameObjectMdt


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
        self.fsm = self.fsm_cls(self)
        self.logic = self.logic_cls(self, conf)
        self.log_mgr = LogMgr(self)
        self.log_mgr.log_conf()
        self.lang_mgr = LangMgr(self)
        self.gfx = self.gfx_cls(self)
        self.phys = self.phys_cls(self)
        self.gui = self.gui_cls(self)
        self.audio = self.audio_cls(self)
        self.ai = self.ai_cls(self)
        self.event = self.event_cls(self)
        self.pause = PauseMgr(self)
        self.font_mgr = FontMgr(self)
        self.server = Server(self)
        self.client = Client(self)
