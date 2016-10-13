'''This module defines the graphics for a track.'''
from panda3d.core import AmbientLight, BitMask32, Spotlight, NodePath
from direct.actor.Actor import Actor
from racing.game.gameobject.gameobject import Gfx


class _Gfx(Gfx):
    '''This class models the graphics component of a track.'''

    def __init__(self, mdt, track_path, callback):
        self.phys_model = None
        self.waypoints = None
        self.ambient_np = None
        self.corners = None
        self.spot_lgt = None
        self.model = None
        Gfx.__init__(self, mdt)
        self.track_path = track_path
        self.callback = callback
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
        path = self.track_path + '/track.bam'
        time = globalClock.getFrameTime()
        loader.loadModel(path, callback=self.__load_coll, extraArgs=[time])

    def __load_coll(self, model, time):
        '''Loads collisions.'''
        curr_t = globalClock.getFrameTime()
        d_t = round(curr_t - time, 2)
        eng.log_mgr.log('loaded track model (%s seconds)' % str(d_t))
        self.model = model
        if model is None:
            self.model = loader.loadModel(self.track_path + '/track')
        path = self.track_path + '/collision'
        loader.loadModel(path, callback=self.__set_submod, extraArgs=[curr_t])

    @staticmethod
    def __flat_sm(submodel):
        '''Flattening of submodels.'''
        s_n = submodel.getName()
        not_logic = s_n not in ['Minimap', 'Starts', 'Waypoints']
        if not_logic and not s_n.startswith('Empty'):
            submodel.flattenLight()

    def __set_submod(self, model, time):
        '''Sets the submodels.'''
        d_t = round(globalClock.getFrameTime() - time, 2)
        eng.log_mgr.log('loaded track collision (%s seconds)' % str(d_t))
        eng.log_mgr.log("retrieve track's info")
        self.phys_model = model
        p_mod = self.phys_model
        corners = ['topleft', 'topright', 'bottomright', 'bottomleft']
        corners = [p_mod.find('**/Minimap' + crn) for crn in corners]
        if not any(corner.isEmpty() for corner in corners):
            self.corners = [corner.get_pos() for corner in corners]
        for submodel in self.model.getChildren() + p_mod.getChildren():
            self.__flat_sm(submodel)
        self.model.hide(BitMask32.bit(0))

        _waypoints = self.phys_model.findAllMatches('**/Waypoints/Waypoint*')
        self.waypoints = {}
        for w_p in _waypoints:
            wpstr = '**/Waypoints/Waypoint'
            prevs = w_p.getTag('prev').split(',')
            lst_wp = [p_mod.find(wpstr + idx) for idx in prevs]
            self.waypoints[w_p] = lst_wp

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

    def __preload_models(self, models, callback, model='', time=0):
        '''Preloads models.'''
        curr_t = globalClock.getFrameTime()
        d_t = curr_t - time
        if model:
            eng.log_mgr.log('loaded model: %s (%s seconds)' % (model, d_t))
        if models:
            model = models[0]
            game.fsm.curr_load_txt.setText(_('loading model: ') + model)
            path = self.track_path + '/' + model
            if model.endswith('Anim'):
                self.__actors += [Actor(path, {'anim': path + '-Anim'})]
                self.__preload_models(models[1:], callback, model, curr_t)
            else:
                eng.base.loader.loadModel(path)
                self.__preload_models(models[1:], callback, model, curr_t)
        else:
            callback()

    def __process_static(self, model_name, model):
        '''Processes static models.'''
        if model_name not in self.__flat_roots:
            nstr = lambda i: '%s_%s' % (model_name, str(i))
            flat_roots = [self.model.attachNewNode(nstr(i)) for i in range(4)]
            self.__flat_roots[model_name] = flat_roots
        path = self.track_path + '/' + model.getName().split('.')[0][5:]
        eng.base.loader.loadModel(path).reparent_to(model)
        left, right = self.corners[0].getX(), self.corners[1].getX()
        center_x, center_y = (left + right) / 2, (left + right) / 2
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

    def __process_models(self, models, callback):
        '''Processes models.'''
        for model in models:
            model_name = model.getName().split('.')[0][5:]
            if model_name.endswith('Anim'):
                path = self.track_path + '/' + model_name
                self.__actors += [Actor(path, {'anim': path + '-Anim'})]
                self.__actors[-1].loop('anim')
                self.__actors[-1].reparent_to(model)
            else:
                self.__process_static(model_name, model)
        callback()

    def __load_empties(self):
        '''Loads children of the empties.'''
        eng.log_mgr.log('loading track submodels')
        empty_models = self.model.findAllMatches('**/Empty*')

        def load_models():
            '''Loads models.'''
            self.__process_models(list(empty_models), self.flattening)
        names = [model.getName().split('.')[0][5:] for model in empty_models]
        self.__preload_models(list(set(list(names))), load_models)

    def __process_flat_models(self, models, callback):
        '''Processes flat models.'''
        curr_t = globalClock.getFrameTime()
        node = models[0]
        node.clearModelNodes()

        def process_flat(flatten_node, orig_node, model, time, number):
            '''Processes a flattening.'''
            flatten_node.reparent_to(orig_node.get_parent())
            orig_node.remove_node()
            self.__flat_models(models[1:], callback, model, time, number)
        nname = node.get_name()
        game.fsm.curr_load_txt.setText(_('flattening model: ') + nname)
        if game.options['submodels']:
            loader.asyncFlattenStrong(
                node, callback=process_flat, inPlace=False,
                extraArgs=[node, nname, curr_t, len(node.get_children())])
        else:
            len_children = len(node.get_children())
            process_flat(node, NodePath(''), node, curr_t, len_children)
        #len_children = len(node.get_children())
        #node.flattenStrong()
        #process_flat(node, node.get_name(),
        #             globalClock.getFrameTime(), len_children)

    def __flat_models(self, models, callback, model='', time=0, number=0):
        '''Flats models.'''
        curr_t = globalClock.getFrameTime()
        if model:
            str_tmpl = 'flattened model: %s (%s seconds, %s nodes)'
            d_t = round(curr_t - time, 2)
            eng.log_mgr.log(str_tmpl % (model, d_t, number))
        if models:
            self.__process_flat_models(models, callback)
        else:
            callback()

    def flattening(self):
        '''Flattening of the track.'''
        eng.log_mgr.log('track flattening')

        def flatlist(lst):
            '''Flats a list.'''
            return [item for sublist in lst for item in sublist]
        roots = self.__flat_roots.values()
        self.__flat_models(flatlist(roots), self.end_loading)

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
