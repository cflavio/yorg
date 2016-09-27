'''This module provides the engine object.'''
import sys
from direct.gui.DirectFrame import DirectFrame
sys.path.append('./ya2/thirdparty')

from direct.filter.CommonFilters import CommonFilters
from direct.particles.ParticleEffect import ParticleEffect
from direct.showbase.ShowBase import ShowBase
from os import environ, system
from panda3d.bullet import BulletWorld, BulletDebugNode
from panda3d.core import getModelPath, WindowProperties, LightRampAttrib, \
    PandaNode, NodePath, AntialiasAttrib
from webbrowser import open_new_tab
from .pause import pause, resume, get_is_paused
import __builtin__
from .font import FontMgr
from .log import LogMgr
from .lang import LangMgr
from .option import OptionMgr
from .configuration import Configuration


class OnFrame:
    pass


class OnCollision:

    def __init__(self, obj_name):
        self.obj_name = obj_name


class Engine(ShowBase, object):
    '''This class models the engine object.'''

    def __init__(self, configuration=None, domain=''):
        configuration = configuration or Configuration()
        ShowBase.__init__(self)
        __builtin__.eng = self
        self.disableMouse()
        getModelPath().appendDirectory('assets/models')
        self.enableParticles()
        #base.cam.node().getLens().setNearFar(10.0, 1000.0)

        self.render.setShaderAuto()
        self.render.setTwoSided(True)
        if configuration.antialiasing:
            self.render.setAntialias(AntialiasAttrib.MAuto)
        #self.__set_toon()

        self.font_mgr = FontMgr(self)
        self.log_mgr = LogMgr()
        self.log_mgr.log_conf()

        self.lang_mgr = LangMgr(domain, './assets/locale',
                                OptionMgr.get_options()['lang'])

        if self.win:
            try:
                self.set_resolution('x'.join(configuration.win_size.split()))
            except AttributeError:
                pass  # configuration file doesn't exist
            if OptionMgr.get_options()['fullscreen']:
                self.toggle_fullscreen()

            self.win.setCloseRequestEvent('window-closed')
            self.accept('window-closed', self.__on_close)

        self.world_phys = None
        self.collision_objs = None
        self.pause_frame = None
        self.__coll_dct = None
        self.world_np = None
        self.__debug_np = None

    @staticmethod
    def __set_toon():
        '''Sets toon shading.'''
        tempnode = NodePath(PandaNode("temp node"))
        tempnode.setAttrib(LightRampAttrib.makeSingleThreshold(0.5, 0.4))
        tempnode.setShaderAuto()
        base.cam.node().setInitialState(tempnode.getState())
        CommonFilters(base.win, base.cam).setCartoonInk(separation=1)

    def __on_close(self):
        '''Called when the application closes.'''
        if OptionMgr.get_options()['open_browser_at_exit']:
            eng.open_browser('http://www.ya2.it')
        self.closeWindow(self.win)
        sys.exit()

    def toggle_pause(self):
        '''Toggles the pause.'''
        if not get_isPaused():
            self.pause_frame = DirectFrame(
                frameColor=(.3, .3, .3, .7), frameSize=(-1.8, 1.8, -1, 1))
        else:
            self.pause_frame.destroy()
        (resume if get_isPaused() else pause)()

    def init(self):
        '''Inits the engine.'''
        self.collision_objs = []
        self.__coll_dct = {}
        self.world_np = render.attachNewNode('world')
        self.world_phys = BulletWorld()
        self.world_phys.setGravity((0, 0, -9.81))
        debug_node = BulletDebugNode('Debug')
        debug_node.showBoundingBoxes(True)
        self.__debug_np = self.render.attachNewNode(debug_node)
        self.world_phys.setDebugNode(self.__debug_np.node())

    def start(self):
        '''Starts the engine.'''
        self.taskMgr.add(self.__update, 'Engine::update')

    def stop(self):
        '''Stops the engine.'''
        eng.world_phys = None
        eng.world_np.removeNode()
        self.__debug_np.removeNode()

    def __update(self, task):
        '''Called on each frame.'''
        if self.world_phys:
            d_t = globalClock.getDt()
            self.world_phys.doPhysics(d_t, 10, 1/180.0)
            self.__do_collisions()
            self.messenger.send('on_frame')
            return task.cont

    def __do_collisions(self):
        '''Computes the collisions.'''
        to_clear = self.collision_objs[:]
        for obj in self.collision_objs:
            if not obj in self.__coll_dct:
                self.__coll_dct[obj] = []
            result = self.world_phys.contactTest(obj)
            for contact in result.getContacts():
                def process_contact(node):
                    '''Processes a physics contact.'''
                    if node != obj:
                        if obj in to_clear:
                            to_clear.remove(obj)
                        if not node in [coll_pair[0]
                                        for coll_pair in self.__coll_dct[obj]]:
                            self.__coll_dct[obj] += \
                                [(node, globalClock.getFrameTime())]
                            self.messenger.send('on_collision',
                                                [obj, node.getName()])
                process_contact(contact.getNode0())
                process_contact(contact.getNode1())
        for obj in to_clear:
            for coll_pair in self.__coll_dct[obj]:
                if globalClock.getFrameTime() - coll_pair[1] > .25:
                    self.__coll_dct[obj].remove(coll_pair)

    @property
    def resolutions(self):
        '''Available resolutions.'''
        d_i = self.pipe.getDisplayInformation()
        res_values = [
            (d_i.getDisplayModeWidth(idx), d_i.getDisplayModeHeight(idx))
            for idx in range(d_i.getTotalDisplayModes())]
        return ['%dx%d' % (s[0], s[1]) for s in sorted(list(set(res_values)))]

    @property
    def resolution(self):
        '''Current resolution.'''
        win_prop = self.win.get_properties()
        res_x, res_y = win_prop.get_x_size(), win_prop.get_y_size()
        return '%dx%d' % (res_x, res_y)

    @property
    def closest_res(self):
        '''The closest resolution to the current one.'''
        def split_res(res):
            '''Gets the resolution values.'''
            return [int(v) for v in res.split('x')]

        def distance(res):
            '''Distance from a resolution.'''
            curr_res, res = split_res(eng.resolution), split_res(res)
            return abs(res[0] - curr_res[0]) + abs(res[1] - curr_res[1])

        dist_lst = map(distance, eng.resolutions)
        try:
            idx_min = dist_lst.index(min(dist_lst))
            return eng.resolutions[idx_min]
        except ValueError:  # sometimes we have empty resolutions
            return eng.resolution

    def set_resolution(self, res, check=True):
        '''Sets a resolution.'''
        self.log_mgr.log('setting resolution ' + str(res))
        props = WindowProperties()
        props.set_size(*[int(resol) for resol in res.split('x')])
        self.win.request_properties(props)
        if check:
            taskMgr.doMethodLater(
                3.0, self.set_resolution_check, 'resolution check', [res])

    def set_resolution_check(self, res):
        '''Checks the resolution.'''
        self.log_mgr.log('resolutions: %s %s' % (self.resolution, res))
        if self.resolution != res:
            self.log_mgr.log('second attempt: %s %s' % (self.resolution, res))
            self.set_resolution(res, False)

    @staticmethod
    def open_browser(url):
        '''Opens the browser.'''
        if sys.platform.startswith('linux'):
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

    def print_stats(self):
        '''Prints rendering stats.'''
        print '\n\n#####\nrender2d.analyze()'
        self.render2d.analyze()
        print '\n\n#####\nrender.analyze()'
        self.render.analyze()
        print '\n\n#####\nrender2d.ls()'
        self.render2d.ls()
        print '\n\n#####\nrender.ls()'
        self.render.ls()

    @staticmethod
    def particle(path, parent, render_parent, pos, timeout):
        '''Does a particle effect.'''
        par = ParticleEffect()
        par.loadConfig(path)
        par.start(parent=parent, renderParent=render_parent)
        par.setPos(pos)
        taskMgr.doMethodLater(timeout, lambda p: p.cleanup(), 'clear', [par])

    def toggle_debug(self):
        '''Toggles the physics debug.'''
        is_hidden = self.__debug_np.isHidden()
        (self.__debug_np.show if is_hidden else self.__debug_np.hide)()

    def toggle_fullscreen(self):
        '''Toggles the fullscreen.'''
        self.set_resolution(self.closest_res)
        props = WindowProperties()
        props.set_fullscreen(not self.win.is_fullscreen())
        base.win.requestProperties(props)
