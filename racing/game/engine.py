'''This module provides the engine object.'''
from sys import path, platform

from os.path import dirname, realpath
path.append(dirname(realpath(__file__)) + '/thirdparty')

from os import environ, system
from webbrowser import open_new_tab
from direct.gui.DirectFrame import DirectFrame
from direct.showbase.ShowBase import ShowBase
import __builtin__
from .pause import PauseMgr
from .font import FontMgr
from .log import LogMgr
from .lang import LangMgr
from .configuration import Configuration
from .gfx import GfxMgr
from .gui.gui import GuiMgr
from .phys import PhysMgr


class Engine(ShowBase, object):
    '''This class models the engine object.'''

    def __init__(self, configuration=None, lang_path='', domain='', langs=[]):
        self.pause_frame = None
        configuration = configuration or Configuration()
        ShowBase.__init__(self)
        __builtin__.eng = self
        self.pause_mgr = PauseMgr()
        self.gfx_mgr = GfxMgr('assets/models', configuration.antialiasing)
        self.phys_mgr = PhysMgr()
        self.font_mgr = FontMgr()
        self.log_mgr = LogMgr()
        self.log_mgr.log_conf()
        lang = game.options['lang']
        self.lang_mgr = LangMgr(domain, lang_path, langs, lang)
        if self.win:
            self.gui_mgr = GuiMgr('x'.join(configuration.win_size.split()))

    def toggle_pause(self):
        '''Toggles the pause.'''
        p_mgr = self.pause_mgr
        if not p_mgr.get_is_paused():
            frm_opt = {
                'frameColor': (.3, .3, .3, .7),
                'frameSize': (-1.8, 1.8, -1, 1)}
            self.pause_frame = DirectFrame(**frm_opt)
        else:
            self.pause_frame.destroy()
        (p_mgr.resume if p_mgr.get_is_paused() else p_mgr.pause)()

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
        if self.appRunner:
            package = self.appRunner.p3dInfo.FirstChildElement('package')
            return 'version: ' + package.Attribute('version')
        return 'version: source'
