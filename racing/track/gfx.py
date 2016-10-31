from panda3d.core import AmbientLight, BitMask32, Spotlight, NodePath
from direct.actor.Actor import Actor
from racing.game.gameobject import Gfx


class _Gfx(Gfx):

    def __init__(self, mdt, track_path, split_world, submodels):
        self.phys_model = None
        self.waypoints = None
        self.ambient_np = None
        self.corners = None
        self.spot_lgt = None
        self.model = None
        self.split_world = split_world
        self.submodels = submodels
        self.track_path = track_path
        self.__actors = []
        self.__flat_roots = {}
        Gfx.__init__(self, mdt)

    def async_build(self):
        self.__set_model()
        self.__set_light()

    def __set_model(self):
        eng.log_mgr.log('loading track model')
        self.notify('on_loading', _('loading track model'))
        time = globalClock.getFrameTime()
        path = self.track_path + '/track'
        eng.gfx.load_model(path, callback=self.__load_coll, extraArgs=[time])

    def __load_coll(self, model, time):
        curr_t = globalClock.getFrameTime()
        d_t = round(curr_t - time, 2)
        eng.log_mgr.log('loaded track model (%s seconds)' % str(d_t))
        self.model = model
        path = self.track_path + '/collision'
        loader.loadModel(path, callback=self.__set_submod, extraArgs=[curr_t])

    @staticmethod
    def __flat_sm(submodel):
        s_n = submodel.getName()
        not_logic = s_n not in ['Minimap', 'Starts', 'Waypoints']
        if not_logic and not s_n.startswith('Empty'):
            submodel.flattenLight()

    def hide_models(self, models):
        models = self.phys_model.findAllMatches(models)
        map(lambda mod: mod.hide(), models)

    def __set_submod(self, model, time):
        d_t = round(globalClock.getFrameTime() - time, 2)
        eng.log_mgr.log('loaded track collision (%s seconds)' % str(d_t))
        p_mod = self.phys_model = model
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

        models = ['Road', 'Offroad', 'Wall', 'Respawn', 'Slow', 'Goal']
        map(self.hide_models, ['**/%s*' % mod for mod in models])
        (self.__load_empties if self.submodels else self.end_loading)()

    def get_start_pos(self, i):
        start_pos = (0, 0, 0)
        start_pos_hpr = (0, 0, 0)
        node_str = '**/Start' + str(i + 1)
        start_pos_node = self.phys_model.find(node_str)
        if start_pos_node:
            start_pos = self.phys_model.find(node_str).get_pos()
            start_pos_hpr = self.phys_model.find(node_str).get_hpr()
        return start_pos, start_pos_hpr

    def __preload_models(self, models, callback, model='', time=0):
        curr_t = globalClock.getFrameTime()
        d_t = curr_t - time
        if model:
            eng.log_mgr.log('loaded model: %s (%s seconds)' % (model, d_t))
        if not models:
            callback()
            return
        model = models[0]
        self.notify('on_loading', _('loading model: ') + model)
        path = self.track_path + '/' + model
        if model.endswith('Anim'):
            self.__actors += [Actor(path, {'anim': path + '-Anim'})]
            self.__preload_models(models[1:], callback, model, curr_t)
        else:
            eng.base.loader.loadModel(path)
            self.__preload_models(models[1:], callback, model, curr_t)

    def __process_static(self, model_name, model):
        if model_name not in self.__flat_roots:
            nstr = lambda i: '%s_%s' % (model_name, str(i))
            flat_roots = [self.model.attachNewNode(nstr(i)) for i in range(4)]
            self.__flat_roots[model_name] = flat_roots
        path = self.track_path + '/' + model.getName().split('.')[0][5:]
        eng.base.loader.loadModel(path).reparent_to(model)
        corners = ['topleft', 'topright', 'bottomright', 'bottomleft']
        corners = [self.phys_model.find('**/Minimap' + crn) for crn in corners]
        left, right, top, bottom = corners[0].getX(), corners[1].getX(), \
            corners[0].getY(), corners[3].getY()
        #TODO: use self.mdt.phys.lrtb
        center_x, center_y = (left + right) / 2, (top + bottom) / 2
        pos_x, pos_y = model.get_pos()[0], model.get_pos()[1]
        if not game.options['development']['split_world']:
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
        eng.log_mgr.log('loading track submodels')
        empty_models = self.model.findAllMatches('**/Empty*')

        def load_models():
            self.__process_models(list(empty_models), self.flattening)
        names = [model.getName().split('.')[0][5:] for model in empty_models]
        self.__preload_models(list(set(list(names))), load_models)

    def __process_flat_models(self, models, callback):
        curr_t = globalClock.getFrameTime()
        node = models[0]
        node.clearModelNodes()

        def process_flat(flatten_node, orig_node, model, time, number):
            flatten_node.reparent_to(orig_node.get_parent())
            orig_node.remove_node()
            self.__flat_models(models[1:], callback, model, time, number)
        nname = node.get_name()
        self.notify('on_loading', _('flattening model: ') + nname)
        if self.submodels:
            loader.asyncFlattenStrong(
                node, callback=process_flat, inPlace=False,
                extraArgs=[node, nname, curr_t, len(node.get_children())])
        else:
            len_children = len(node.get_children())
            process_flat(node, NodePath(''), node, curr_t, len_children)

    def __flat_models(self, models, callback, model='', time=0, number=0):
        if model:
            str_tmpl = 'flattened model: %s (%s seconds, %s nodes)'
            d_t = round(globalClock.getFrameTime() - time, 2)
            eng.log_mgr.log(str_tmpl % (model, d_t, number))
        if models:
            self.__process_flat_models(models, callback)
        else:
            callback()

    def flattening(self):
        eng.log_mgr.log('track flattening')
        roots = self.__flat_roots.values()
        self.__flat_models(eng.logic.flatlist(roots), self.end_loading)

    def end_loading(self):
        self.model.prepareScene(eng.base.win.getGsg())
        #taskMgr.doMethodLater(.01, lambda task: self.callback(), 'callback')
        Gfx.async_build(self)

    def __set_light(self):
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
        self.model.removeNode()
        self.phys_model.removeNode()
        eng.base.render.clearLight(self.ambient_np)
        eng.base.render.clearLight(self.spot_lgt)
        self.ambient_np.removeNode()
        #self.spot_lgt.removeNode()
