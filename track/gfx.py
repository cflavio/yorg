from panda3d.core import AmbientLight, BitMask32, Spotlight, TextNode
from direct.actor.Actor import Actor
from ya2.gameobject import Gfx
from direct.gui.OnscreenText import OnscreenText


class _Gfx(Gfx):
    '''This class models the graphics component of a track.'''

    def __init__(self, mdt, track_path, cb):
        Gfx.__init__(self, mdt)
        self.track_path = track_path
        self.cb = cb
        self.__set_model()
        self.__set_light()
        #eng.cam.setPos(0, -40, 50)
        #eng.cam.lookAt(0, 0, 0)

    def __set_model(self):
        eng.log_mgr.log('loading track model')
        game.fsm.curr_load_txt.setText(_('loading track model'))
        loader.loadModel(self.track_path + '/track',
                         callback=self.__set_submodels,
                         extraArgs=[globalClock.getFrameTime()])

    def __set_submodels(self, model, time):
        eng.log_mgr.log('loaded track model (%s seconds)' % str(round(globalClock.getFrameTime() - time, 2)))
        eng.log_mgr.log("retrieve track's info")
        self.model = model
        for submodel in self.model.getChildren():
            if submodel.getName() not in ['Minimap', 'Starts', 'Waypoints'] \
                    and not submodel.getName().startswith('Empty'):
                submodel.flattenLight()
        self.model.hide(BitMask32.bit(0))

        waypoints = self.model.findAllMatches('**/Waypoints/Waypoint*')
        waypoints = [wp for wp in waypoints]
        self.waypoints = {}
        for wp in waypoints:
            lst_wp = [self.model.find('**/Waypoints/Waypoint' + idx)
                      for idx in wp.getTag('prev').split(',')]
            self.waypoints[wp] = lst_wp

        road_models = self.model.findAllMatches('**/Road*')
        map(lambda mod: mod.hide(), road_models)
        offroad_models = self.model.findAllMatches('**/Offroad*')
        map(lambda mod: mod.hide(), offroad_models)
        wall_models = self.model.findAllMatches('**/Wall*')
        map(lambda mod: mod.hide(), wall_models)
        respawn_models = self.model.findAllMatches('**/Respawn*')
        map(lambda mod: mod.hide(), respawn_models)
        slow_models = self.model.findAllMatches('**/Slow*')
        map(lambda mod: mod.hide(), slow_models)
        goal = self.model.find('**/Goal')
        if goal:
            goal.hide()
        self.__load_empties(self.end_loading)

    def end_loading(self):
        start_pos = self.model.find('**/Start1')
        if start_pos:
            self.start_pos = self.model.find('**/Start1').get_pos()
            self.start_pos_hpr = self.model.find('**/Start1').get_hpr()
        else:
            self.start_pos = (0, 0, 0)
            self.start_pos_hpr = (0, 0, 0)
        #self.model.clearModelNodes()
        #self.model.flattenStrong()
        self.model.prepareScene(eng.win.getGsg())
        taskMgr.doMethodLater(.01, lambda task: self.cb(), 'callback')

    def __load_empties(self, end_loading):
        eng.log_mgr.log('loading track submodels')
        empty_models = self.model.findAllMatches('**/Empty*')
        self.__actors = []
        self.__flat_roots = {}
        def preload_models(models, cb, model='', time=0):
            if model:
                eng.log_mgr.log('loaded model: %s (%s seconds)' % (model, globalClock.getFrameTime() - time))
            if models:
                model = models[0]
                game.fsm.curr_load_txt.setText(_('loading model: ') + model)
                if model.endswith('Anim'):
                    self.__actors += [Actor(self.track_path + '/' + model, {
                        'anim': self.track_path + '/' + model + '-Anim'})]
                    preload_models(models[1:], cb, model, globalClock.getFrameTime())
                else:
                    path = self.track_path + '/' + model
                    eng.loader.loadModel(path)
                    preload_models(models[1:], cb, model, globalClock.getFrameTime())
            else:
                cb()

        def process_models(models, cb):
            for model in models:
                model_name = model.getName().split('.')[0][5:]
                if model_name.endswith('Anim'):
                    self.__actors += [Actor(self.track_path + '/' + model_name, {
                        'anim': self.track_path + '/' + model_name + '-Anim'})]
                    self.__actors[-1].loop('anim')
                    self.__actors[-1].reparent_to(model)
                else:
                    if model_name not in self.__flat_roots:
                        flat_root = self.model.attachNewNode(model_name)
                        self.__flat_roots[model_name] = flat_root
                    path = self.track_path + '/' + model.getName().split('.')[0][5:]
                    child = eng.loader.loadModel(path)
                    child.reparent_to(model)
                    model.reparentTo(self.__flat_roots[model_name])
            cb()
        def load_models():
            process_models(list(empty_models), self.flattening)
        names = [model.getName().split('.')[0][5:] for model in empty_models]
        preload_models(list(set(list(names))), load_models)

    def flattening(self):
        eng.log_mgr.log('track flattening')
        def flat_models(models, cb, model='', time=0, number=0):
            if model:
                eng.log_mgr.log('flattened model: %s (%s seconds, %s nodes)' % (model, round(globalClock.getFrameTime() - time, 2), number))
            if models:
                node = models[0]
                node.clearModelNodes()
                def process_flat(flatten_node, model, time, number):
                    flat_models(models[1:], cb, model, time, number)
                game.fsm.curr_load_txt.setText(_('flattening model: ') + node.get_name())
                loader.asyncFlattenStrong(
                    node,
                    callback=process_flat,
                    extraArgs=[node.get_name(),
                               globalClock.getFrameTime(),
                               len(node.get_children())])  # it doesn't work
                #node.flattenStrong()
                #process_flat(node)
            else:
                cb()
        flat_models(self.__flat_roots.values(), self.end_loading)

    def __set_light(self):
        eng.render.clearLight()

        ambient_lgt = AmbientLight('ambient light')
        ambient_lgt.setColor((.7, .7, .55, 1))
        self.ambient_np = render.attachNewNode(ambient_lgt)
        render.setLight(self.ambient_np)

        #directional_lgt = DirectionalLight('directional light')
        #directional_lgt.setDirection((.5, .5, -1))
        #directional_lgt.setColor((.75, .75, .75, 1))
        #self.directional_np = eng.render.attachNewNode(directional_lgt)
        #eng.render.setLight(self.directional_np)

        self.spot_lgt = render.attachNewNode(Spotlight('Spot'))
        self.spot_lgt.node().setScene(render)
        self.spot_lgt.node().setShadowCaster(True, 1024, 1024)
        self.spot_lgt.node().getLens().setFov(40)
        self.spot_lgt.node().getLens().setNearFar(20, 200)
        self.spot_lgt.node().setCameraMask(BitMask32.bit(0))
        self.spot_lgt.setPos(50, -80, 80)
        self.spot_lgt.lookAt(0, 0, 0)
        render.setLight(self.spot_lgt)
        render.setShaderAuto()

    def destroy(self):
        '''The destroyer.'''
        self.model.removeNode()
        eng.render.clearLight(self.ambient_np)
        eng.render.clearLight(self.spot_lgt)
        self.ambient_np.removeNode()
        #self.spot_lgt.removeNode()
