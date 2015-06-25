import sys
sys.path.append('./ya2/thirdparty')

from datetime import datetime
from direct.directnotify.DirectNotify import DirectNotify
from direct.filter.CommonFilters import CommonFilters
from direct.showbase.ShowBase import ShowBase
from gettext import install, translation
from os import environ, system
from panda3d.bullet import BulletWorld, BulletDebugNode
from panda3d.core import getModelPath, WindowProperties, LightRampAttrib, \
    PandaNode, NodePath, AntialiasAttrib
from panda3d.core import loadPrcFileData
from webbrowser import open_new_tab
import __builtin__
import yaml
import platform
import sys


class OnFrame:
    pass


class OnCollision:

    def __init__(self, obj_name):
        self.obj_name = obj_name


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
        self.log('operative system: '+platform.system()+' '+platform.release())
        if eng.win:
            prop = eng.win.get_properties()
            self.log('fullscreen: '+str(prop.get_fullscreen()))
            resolution = (prop.get_x_size(), prop.get_y_size())
            self.log('resolution: %sx%s' % resolution)


class LangMgr(object):

    lang_list = ['en', 'it']
    languages = ['English', 'Italiano']

    def __init__(self, domain, path, lang_index):
        self.__domain = domain
        self.__path = path
        install(domain, path, unicode=1)
        self.set_lang(self.lang_list[lang_index])

    def set_lang(self, lang):
        self.curr_lang = lang
        try:
            lang = translation(self.__domain, self.__path, languages=[lang])
            lang.install(unicode=1)
        except IOError:
            install(self.__domain, self.__path, unicode=1)


class OptionMgr:

    @staticmethod
    def get_options():
        try:
            with open('options.yml') as opt_file:
                conf = yaml.load(opt_file)
        except IOError:
            conf = {
            'lang': 0,
            'volume': 1,
            'fullscreen': 0,
            'resolution': None,
            'aa': 0}
        return conf

    @staticmethod
    def set_options(conf):
        with open('options.yml', 'w') as opt_file:
            yaml.dump(conf, opt_file, default_flow_style=False)


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
                 fullscreen=False, cursor_hidden=False, sync_video=True,
                 antialiasing=False):
        self.fps = fps
        self.win_size = win_size
        self.win_title = win_title
        self.fullscreen = fullscreen
        self.cursor_hidden = cursor_hidden
        self.sync_video = sync_video
        self.antialiasing = antialiasing
        self.configure()

    @staticmethod
    def __set(key, value):
        loadPrcFileData('', key+' '+str(value))

    def configure(self):
        self.__set('show-frame-rate-meter', int(self.fps))
        if self.win_size:
            self.__set('win-size', self.win_size)
        self.__set('window-title', self.win_title)
        self.__set('fullscreen', int(self.fullscreen))
        self.__set('cursor-hidden', int(self.cursor_hidden))
        self.__set('sync-video', int(self.sync_video))
        if self.antialiasing:
            self.__set('framebuffer-multisample', 1)
            self.__set('multisamples', 2)
        LogMgr.configure()


class Engine(ShowBase, object):

    def __init__(self, configuration=None, domain=''):
        configuration = configuration or Configuration()
        ShowBase.__init__(self)
        __builtin__.eng = self
        self.disableMouse()
        getModelPath().appendDirectory('assets/models')

        self.render.setShaderAuto()
        if configuration.antialiasing:
            self.render.setAntialias(AntialiasAttrib.MAuto)
        #self.__set_toon()

        self.world_np = render.attachNewNode('world')

        self.collision_objs = []
        self.__coll_dct = {}
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

        self.lang_mgr = LangMgr(domain, './assets/locale',
                                OptionMgr.get_options()['lang'])

        if self.win:
            self.set_resolution(self.resolution)

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

    def __update(self, task):
        dt = globalClock.getDt()
        self.world_phys.doPhysics(dt, 5, 1/60.0)
        self.__do_collisions()
        self.messenger.send('on_frame')
        return task.cont

    def __do_collisions(self):
        to_clear = self.collision_objs[:]
        for obj in self.collision_objs:
            if not obj in self.__coll_dct:
                self.__coll_dct[obj] = []
            result = self.world_phys.contactTest(obj)
            for contact in result.getContacts():
                def process_contact(node):
                    if node != obj:
                        if obj in to_clear:
                            to_clear.remove(obj)
                        if not node in [coll_pair[0] for coll_pair in self.__coll_dct[obj]]:
                            self.__coll_dct[obj] += [(node, globalClock.getFrameTime())]
                            self.messenger.send('on_collision', [node.getName()])
                process_contact(contact.getNode0())
                process_contact(contact.getNode1())
        for obj in to_clear:
            for coll_pair in self.__coll_dct[obj]:
                if globalClock.getFrameTime() - coll_pair[1] > .25:
                    self.__coll_dct[obj].remove(coll_pair)

    @property
    def resolutions(self):
        di = self.pipe.getDisplayInformation()
        res_values = [
            (di.getDisplayModeWidth(idx), di.getDisplayModeHeight(idx))
            for idx in range(di.getTotalDisplayModes())]
        return ['%dx%d' % (s[0], s[1]) for s in sorted(list(set(res_values)))]

    @property
    def resolution(self):
        win_prop = self.win.get_properties()
        res_x, res_y = win_prop.get_x_size(), win_prop.get_y_size()
        return '%dx%d' % (res_x, res_y)

    def closest_res(self):
        def split_res(res):
            return [int(v) for v in res.split('x')]

        def distance(res):
            curr_res, res = split_res(eng.resolution), split_res(res)
            return abs(res[0] - curr_res[0]) + abs(res[1] - curr_res[1])

        dist_lst = map(distance, eng.resolutions)
        idx_min = dist_lst.index(min(dist_lst))
        return eng.resolutions[idx_min]

    def set_resolution(self, res):
        props = WindowProperties()
        props.set_size(*[int(res) for res in res.split('x')])
        self.win.request_properties(props)

    def open_browser(self, url):
        if sys.platform.startswith('linux'):
            environ['LD_LIBRARY_PATH'] = ''
            system('xdg-open '+url)
        else:
            open_new_tab(url)

    @property
    def version(self):
        version = 'version: source'
        if self.appRunner:
            package = self.appRunner.p3dInfo.FirstChildElement('package')
            version = 'version: ' + package.Attribute('version')
        return version

    def toggle_debug(self):
        is_hidden = self.__debug_np.isHidden()
        (self.__debug_np.show if is_hidden else self.__debug_np.hide)()

    def toggle_fullscreen(self, state):
        self.set_resolution(self.closest_res())
        props = WindowProperties()
        props.set_fullscreen(not self.win.is_fullscreen())
        base.win.requestProperties(props)