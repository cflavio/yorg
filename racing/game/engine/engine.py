'''This module provides the engine object.'''
from sys import path

from os.path import dirname, realpath
path.append(dirname(realpath(__file__)) + '/thirdparty')

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
from ..gameobject.gameobject import GameObjectMdt


class EngineBase(ShowBase):
    '''PAnda3D ShowBase.'''

    pass


class Engine(GameObjectMdt):
    '''This class models the GameObject.'''
    gfx_cls = EngineGfx
    gui_cls = EngineGui
    logic_cls = EngineLogic
    phys_cls = EnginePhys
    event_cls = EngineEvent

    def __init__(self, conf=None):
        __builtin__.eng = self
        self.base = EngineBase()
        self.fsm = self.fsm_cls(self)
        self.logic = self.logic_cls(self, conf)
        self.log_mgr = LogMgr()
        self.log_mgr.log_conf()
        self.lang_mgr = LangMgr()
        self.gfx = self.gfx_cls(self)
        self.phys = self.phys_cls(self)
        self.gui = self.gui_cls(self)
        self.audio = self.audio_cls(self)
        self.ai = self.ai_cls(self)
        self.event = self.event_cls(self)
        self.pause_mgr = PauseMgr()
        self.font_mgr = FontMgr()
