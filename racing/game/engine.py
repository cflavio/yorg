'''This module provides the engine object.'''
from sys import path, platform, exit
from os import environ, system
from webbrowser import open_new_tab
from panda3d.core import LightRampAttrib, \
    PandaNode, NodePath, AntialiasAttrib
from direct.gui.DirectFrame import DirectFrame
from direct.filter.CommonFilters import CommonFilters
from direct.particles.ParticleEffect import ParticleEffect
from direct.showbase.ShowBase import ShowBase
import __builtin__
from .pause import pause, resume, get_is_paused
from .font import FontMgr
from .log import LogMgr
from .lang import LangMgr
from .option import OptionMgr
from .configuration import Configuration
from .gfx import GfxMgr
from .gui.gui import GuiMgr
from .phys import PhysMgr


path.append('./ya2/thirdparty')


class Engine(ShowBase, object):
    '''This class models the engine object.'''

    def __init__(self, configuration=None, domain=''):
        self.pause_frame = None
        configuration = configuration or Configuration()
        ShowBase.__init__(self)
        __builtin__.eng = self
        self.gfx_mgr = GfxMgr(configuration.antialiasing)
        self.phys_mgr = PhysMgr()
        self.font_mgr = FontMgr()
        self.log_mgr = LogMgr()
        self.log_mgr.log_conf()
        lang = OptionMgr.get_options()['lang']
        self.lang_mgr = LangMgr(domain, './assets/locale', lang)
        if self.win:
            self.gui_mgr = GuiMgr('x'.join(configuration.win_size.split()))

    def toggle_pause(self):
        '''Toggles the pause.'''
        if not get_is_paused():
            frm_opt = {}
            frm_opt['frameColor'] = (.3, .3, .3, .7),
            frm_opt['frameSize'] = (-1.8, 1.8, -1, 1)
            self.pause_frame = DirectFrame(**frm_opt)
        else:
            self.pause_frame.destroy()
        (resume if get_is_paused() else pause)()

    @staticmethod
    def open_browser(url):
        '''Opens the browser.'''
        if platform.startswith('linux'):
            environ['LD_LIBRARY_PATH'] = ''
            system('xdg-open '+url)
        else:
            open_new_tab(url)

    @property
    def version(self):
        '''The current software version.'''
        version = 'version: source'
        if self.appRunner:
            package = self.appRunner.p3dInfo.FirstChildElement('package')
            version = 'version: ' + package.Attribute('version')
        return version

