'''This module defines the graphics for a track.'''
from panda3d.core import AmbientLight, BitMask32, Spotlight, NodePath
from direct.actor.Actor import Actor
from racing.game.gameobject.gameobject import Gfx


class _Gfx(Gfx):
    '''This class models the graphics component of a track.'''

    def __init__(self, mdt, track_path, callback):
        Gfx.__init__(self, mdt)
        self.track_path = track_path
        self.callback = callback
        self.phys_model = None
        self.waypoints = None
        self.ambient_np = None
        self.corners = None
        self.spot_lgt = None
        self.model = None
        self.__actors = []
        self.__flat_roots = {}
        self.__set_model()
        self.__set_light()
        #eng.cam.setPos(0, -40, 50)
        #eng.cam.lookAt(0, 0, 0)

    def __set_model(self):
        '''Sets the model.'''
        eng.log_mgr.log('loading track model')
        game.fsm.curr_load_txt.setText(_('loading track model'))
        loader.loadModel(self.track_path + '/track.bam',
                         callback=self.__load_collisions,
                         extraArgs=[globalClock.getFrameTime()])

    def __load_collisions(self, model, time):
        '''Loads collisions.'''
        eng.log_mgr.log('loaded track model (%s seconds)' %
                        str(round(globalClock.getFrameTime() - time, 2)))
        self.model = model
        if model is None:
            self.model = loader.loadModel(self.track_path + '/track')
        loader.loadModel(self.track_path + '/collision',
                         callback=self.__set_submodels,
                         extraArgs=[globalClock.getFrameTime()])

    def __set_submodels(self, model, time):
        '''Sets the submodels.'''
        eng.log_mgr.log('loaded track collision (%s seconds)' %
                        str(round(globalClock.getFrameTime() - time, 2)))
        eng.log_mgr.log("retrieve track's info")
        self.phys_model = model
        corners = ['topleft', 'topright', 'bottomright', 'bottomleft']
        corners = [self.mdt.gfx.phys_model.find('**/Minimap'+corner)
                   for corner in corners]
        if not any(corner.isEmpty() for corner in corners):
            self.corners = [corner.get_pos() for corner in corners]
        for submodel in self.model.getChildren() + \
                self.phys_model.getChildren():
            if submodel.getName() not in ['Minimap', 'Starts', 'Waypoints'] \
                    and not submodel.getName().startswith('Empty'):
                submodel.flattenLight()
        self.model.hide(BitMask32.bit(0))

        _waypoints = self.phys_model.findAllMatches('**/Waypoints/Waypoint*')
        self.waypoints = {}
        for waypoint in _waypoints:
            lst_wp = [self.phys_model.find('**/Waypoints/Waypoint' + idx)
                      for idx in waypoint.getTag('prev').split(',')]
            self.waypoints[waypoint] = lst_wp

        road_models = self.phys_model.findAllMatches('**/Road*')
        map(lambda mod: mod.hide(), road_models)
        offroad_models = self.phys_model.findAllMatches('**/Offroad*')
        map(lambda mod: mod.hide(), offroad_models)
        wall_models = self.phys_model.findAllMatches('**/Wall*')
        map(lambda mod: mod.hide(), wall_models)
        respawn_models = self.phys_model.findAllMatches('**/Respawn*')
        map(lambda mod: mod.hide(), respawn_models)
        slow_models = self.phys_model.findAllMatches('**/Slow*')
        map(lambda mod: mod.hide(), slow_models)
        goal = self.phys_model.find('**/Goal')
        if goal:
            goal.hide()
        self.__load_empties()

    def get_start_pos(self, i):
        '''Returns the i-th start position.'''
        node_str = '**/Start' + str(i + 1)
        start_pos_node = self.phys_model.find(node_str)
        if start_pos_node:
            start_pos = self.phys_model.find(node_str).get_pos()
            start_pos_hpr = self.phys_model.find(node_str).get_hpr()
        else:
            start_pos = (0, 0, 0)
            start_pos_hpr = (0, 0, 0)
        return start_pos, start_pos_hpr

    def end_loading(self):
        '''Called at the end of the loading.'''
        #self.model.clearModelNodes()
        #self.model.flattenStrong()
        self.model.prepareScene(eng.base.win.getGsg())
        taskMgr.doMethodLater(.01, lambda task: self.callback(), 'callback')

    def __load_empties(self):
        '''Loads children of the empties.'''
        eng.log_mgr.log('loading track submodels')
        empty_models = self.model.findAllMatches('**/Empty*')

        def preload_models(models, callback, model='', time=0):
            '''Preloads models.'''
            if model:
                eng.log_mgr.log('loaded model: %s (%s seconds)' %
                                (model, globalClock.getFrameTime() - time))
            if models:
                model = models[0]
                game.fsm.curr_load_txt.setText(_('loading model: ') + model)
                if model.endswith('Anim'):
                    self.__actors += [Actor(self.track_path + '/' + model, {
                        'anim': self.track_path + '/' + model + '-Anim'})]
                    preload_models(models[1:], callback, model,
                                   globalClock.getFrameTime())
                else:
                    path = self.track_path + '/' + model
                    eng.base.loader.loadModel(path)
                    preload_models(models[1:], callback, model,
                                   globalClock.getFrameTime())
            else:
                callback()

        def process_models(models, callback):
            '''Processes models.'''
            for model in models:
                model_name = model.getName().split('.')[0][5:]
                if model_name.endswith('Anim'):
                    self.__actors += [
                        Actor(self.track_path + '/' + model_name, {
                            'anim': self.track_path + '/' +
                                model_name + '-Anim'})]
                    self.__actors[-1].loop('anim')
                    self.__actors[-1].reparent_to(model)
                else:
                    if model_name not in self.__flat_roots:
                        flat_roots = [
                            self.model.attachNewNode(
                                '%s_%s' % (model_name, str(i)))
                            for i in range(4)]
                        self.__flat_roots[model_name] = flat_roots
                    path = self.track_path + '/' + \
                        model.getName().split('.')[0][5:]
                    child = eng.base.loader.loadModel(path)
                    child.reparent_to(model)
                    left = self.corners[0].getX()
                    right = self.corners[1].getX()
                    center_x = (left + right) / 2
                    center_y = (left + right) / 2
                    pos_x, pos_y = model.get_pos()[0], model.get_pos()[1]
                    if not game.options['split_world']:
                        parent = self.__flat_roots[model_name][0]
                    elif pos_x < center_x and pos_y < center_y:
                        parent = self.__flat_roots[model_name][0]
                    elif pos_x >= center_x and pos_y < center_y:
                        parent = self.__flat_roots[model_name][1]
                    elif pos_x < center_x and pos_y >= center_y:
                        parent = self.__flat_roots[model_name][2]
                    else:
                        parent = self.__flat_roots[model_name][3]
                    model.reparentTo(parent)
            callback()

        def load_models():
            '''Loads models.'''
            process_models(list(empty_models), self.flattening)
        names = [model.getName().split('.')[0][5:] for model in empty_models]
        preload_models(list(set(list(names))), load_models)

    def flattening(self):
        '''Flattening of the track.'''
        eng.log_mgr.log('track flattening')

        def flat_models(models, callback, model='', time=0, number=0):
            '''Flats models.'''
            if model:
                eng.log_mgr.log(
                    'flattened model: %s (%s seconds, %s nodes)' %
                    (model,
                     round(globalClock.getFrameTime() - time, 2), number))
            if models:
                node = models[0]
                node.clearModelNodes()

                def process_flat(flatten_node, orig_node, model, time, number):
                    '''Processes a flattening.'''
                    flatten_node.reparent_to(orig_node.get_parent())
                    orig_node.remove_node()
                    flat_models(models[1:], callback, model, time, number)
                game.fsm.curr_load_txt.setText(
                    _('flattening model: ') + node.get_name())
                if game.options['submodels']:
                    loader.asyncFlattenStrong(
                        node,
                        callback=process_flat,
                        inPlace=False,
                        extraArgs=[node,
                                   node.get_name(),
                                   globalClock.getFrameTime(),
                                   len(node.get_children())])  # doesn't work
                else:
                    len_children = len(node.get_children())
                    process_flat(node, NodePath(''), node,
                                 globalClock.getFrameTime(), len_children)
                #len_children = len(node.get_children())
                #node.flattenStrong()
                #process_flat(node, node.get_name(),
                #             globalClock.getFrameTime(), len_children)
            else:
                callback()

        def flatlist(lst):
            '''Flats a list.'''
            return [item for sublist in lst for item in sublist]
        flat_models(flatlist(self.__flat_roots.values()), self.end_loading)

    def __set_light(self):
        '''Sets the lighting.'''
        eng.base.render.clearLight()

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
        self.phys_model.removeNode()
        eng.base.render.clearLight(self.ambient_np)
        eng.base.render.clearLight(self.spot_lgt)
        self.ambient_np.removeNode()
        #self.spot_lgt.removeNode()
