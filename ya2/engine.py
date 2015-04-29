import __builtin__
from datetime import datetime
from direct.directnotify.DirectNotify import DirectNotify
from direct.filter.CommonFilters import CommonFilters
from direct.showbase.ShowBase import ShowBase
from gettext import install, translation
from os import environ
from panda3d.bullet import BulletWorld, BulletDebugNode
from panda3d.core import getModelPath, WindowProperties, LightRampAttrib, \
    PandaNode, NodePath
from panda3d.core import loadPrcFileData
from platform import system, release
from sys import platform
import sys
from webbrowser import open_new_tab

from ya2.decorators.access import auto_properties
from ya2.decorators.sender import sender_dec


class OnFrame:
    pass


class LogMgr:

    def __init__(self):
        self.__notify = DirectNotify().newCategory('ya2')

    @staticmethod
    def configure():
        loadPrcFileData('', 'notify-level-ya2 info')

    def log(self, msg):
        self.__notify.info(datetime.now().strftime("%H:%M:%S") + ' ' + msg)

    def log_conf(self):
        self.log('version: '+eng.version)
        self.log('operative system: '+system()+' '+release())
        if eng.win:
            prop = eng.win.get_properties()
            self.log('fullscreen: '+str(prop.get_fullscreen()))
            resolution = (prop.get_x_size(), prop.get_y_size())
            self.log('resolution: %sx%s' % resolution)


class LangMgr(object):

    def __init__(self, domain, path, lang):
        self.__domain = domain
        self.__path = path
        install(domain, path, unicode=1)
        self.set_lang(lang)

    def set_lang(self, lang):
        self.curr_lang = lang
        try:
            lang = translation(self.__domain, self.__path, languages=[lang])
            lang.install(unicode=1)
        except IOError:
            install(self.__domain, self.__path, unicode=1)


class FontMgr:

    def __init__(self, eng):
        self.__fonts = {}
        self.__eng = eng

    def load_font(self, path):
        if path not in self.__fonts:
            self.__fonts[path] = self.__eng.loader.loadFont(path)
            self.__fonts[path].setPixelsPerUnit(60)
        return self.__fonts[path]


class Configuration:

    def __init__(self, fps=False, win_size='1280 720', win_title='Ya2',
                 fullscreen=False, cursor_hidden=False, sync_video=True):
        self.__fps = fps
        self.__win_size = win_size
        self.__win_title = win_title
        self.__fullscreen = fullscreen
        self.__cursor_hidden = cursor_hidden
        self.__sync_video = sync_video
        self.configure()

    @staticmethod
    def __set(key, value):
        loadPrcFileData('', key+' '+str(value))

    def configure(self):
        self.__set('show-frame-rate-meter', int(self.__fps))
        self.__set('win-size', self.__win_size)
        self.__set('window-title', self.__win_title)
        self.__set('fullscreen', int(self.__fullscreen))
        self.__set('cursor-hidden', int(self.__cursor_hidden))
        self.__set('sync-video', int(self.__sync_video))
        self.__set('aspect-ratio', 1.77778)
        self.__set('bullet-enable-contact-events', 'true')
        LogMgr.configure()


@auto_properties
class Engine(ShowBase, object):

    def __init__(self, configuration=None, domain=''):
        configuration = configuration or Configuration()
        ShowBase.__init__(self)
        __builtin__.eng = self
        self.disableMouse()
        getModelPath().appendDirectory('assets/models')

        self.render.setShaderAuto()

        self.__set_toon()

        self.world_np = render.attachNewNode('world')
        self.messenger.send = sender_dec(self.messenger.send)

        self.world_phys = BulletWorld()
        self.world_phys.setGravity((0, 0, -9.81))
        debug_node = BulletDebugNode('Debug')
        debug_node.showBoundingBoxes(True)
        self.__debug_np = self.render.attachNewNode(debug_node)
        self.world_phys.setDebugNode(self.__debug_np.node())

        self.taskMgr.add(self.__update, 'Engine::update')

        self.font_mgr = FontMgr(self)
        self.log_mgr = LogMgr()
        self.log_mgr.log_conf()
        self.lang_mgr = LangMgr(domain, './assets/locale', 'en')

        self.accept('window-event', self.__on_resize)

        if self.win:
            self.set_resolution(self.get_resolution())

            self.win.setCloseRequestEvent('window-closed')
            self.accept('window-closed', self.__on_close)

    def __set_toon(self):
        tempnode = NodePath(PandaNode("temp node"))
        tempnode.setAttrib(LightRampAttrib.makeSingleThreshold(0.5, 0.4))
        tempnode.setShaderAuto()
        base.cam.node().setInitialState(tempnode.getState())
        CommonFilters(base.win, base.cam).setCartoonInk(separation=1)

    def __on_close(self):
        self.closeWindow(self.win)
        sys.exit()

    def __on_resize(self, a):
        props = self.win.get_properties()
        res_x = props.get_x_size()
        res_y = props.get_y_size()
        if float(res_x) / res_y < 1.7777:
            dx, dy = 0, .28 * res_x / res_y
        else:
            dx, dy = float(float(res_x - res_y * 1.7777)/2) / res_x, .5
        regions = [d for d in base.win.get_display_regions()
                   if d.getSort() != -50]
        for region in regions:
            region.setDimensions(dx, 1-dx, .5-dy, .5+dy)

    def __update(self, task):
        dt = globalClock.getDt()
        self.world_phys.doPhysics(dt)
        self.messenger.send(OnFrame())
        return task.cont

    def get_resolutions(self):
        di = self.pipe.getDisplayInformation()
        res_values = [
            (di.getDisplayModeWidth(idx), di.getDisplayModeHeight(idx))
            for idx in range(di.getTotalDisplayModes())]
        return ['%dx%d' % (s[0], s[1]) for s in sorted(list(set(res_values)))]

    def get_resolution(self):
        win_prop = self.win.get_properties()
        res_x, res_y = win_prop.get_x_size(), win_prop.get_y_size()
        return '%dx%d' % (res_x, res_y)

    def set_resolution(self, res):
        props = WindowProperties()
        props.set_size(*[int(res) for res in res.split('x')])
        self.win.request_properties(props)

        # if we don't have the black-border display region, create it
        if not any(d.getSort() == -50 for d in base.win.get_display_regions()):
            display_reg = self.win.makeDisplayRegion()
            display_reg.setClearColorActive(True)
            display_reg.setClearColor((0, 0, 0, 1))
            display_reg.setSort(-50)
        base.cam.node().getDisplayRegion(0).setClearColorActive(True)
        base.cam.node().getDisplayRegion(0).setClearColor((.45, .45, .55, 1))

    def open_browser(self, url):
        if platform.startswith('linux'):
            environ['LD_LIBRARY_PATH'] = ''
            system('xdg-open '+url)
        else:
            open_new_tab(url)

    def get_version(self):
        version = 'version: source'
        if self.appRunner:
            package = self.appRunner.p3dInfo.FirstChildElement('package')
            version = 'version: ' + package.Attribute('version')
        return version

    def toggle_debug(self):
        is_hidden = self.__debug_np.isHidden()
        (self.__debug_np.show if is_hidden else self.__debug_np.hide)()

    def toggle_fullscreen(self, state):
        props = WindowProperties()
        props.set_fullscreen(not self.win.is_fullscreen())
        base.win.requestProperties(props)