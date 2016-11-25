from panda3d.core import AmbientLight, BitMask32, Spotlight, NodePath
from direct.actor.Actor import Actor
from racing.game.gameobject import Gfx


class TrackGfx(Gfx):

    def __init__(self, mdt, split_world, submodels):
        self.ambient_np = None
        self.spot_lgt = None
        self.model = None
        self.split_world = split_world
        self.submodels = submodels
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
        path = self.mdt.path + '/track'
        eng.gfx.load_model(path, callback=self.__set_submod, extraArgs=[time])

    def __set_submod(self, model, time):
        d_t = round(globalClock.getFrameTime() - time, 2)
        eng.log_mgr.log('loaded track model (%s seconds)' % str(d_t))
        self.model = model
        for submodel in self.model.getChildren():
            self.__flat_sm(submodel)
        self.model.hide(BitMask32.bit(0))
        (self.__load_empties if self.submodels else self.end_loading)()

    @staticmethod
    def __flat_sm(submodel):
        s_n = submodel.getName()
        if not s_n.startswith('Empty'):
            submodel.flattenLight()

    def __load_empties(self):
        eng.log_mgr.log('loading track submodels')
        empty_models = self.model.findAllMatches('**/Empty*')

        def load_models():
            self.__process_models(list(empty_models))
        names = [model.getName().split('.')[0][5:] for model in empty_models]
        self.__preload_models(list(set(list(names))), load_models)

    def __preload_models(self, models, callback, model='', time=0):
        curr_t = globalClock.getFrameTime()
        d_t = curr_t - time
        if model:
            eng.log_mgr.log('loaded model: %s (%s seconds)' % (model, d_t))
        if not models:
            callback()
            return
        model = models.pop(0)
        self.notify('on_loading', _('loading model: ') + model)
        path = self.mdt.path + '/' + model
        if model.endswith('Anim'):
            self.__actors += [Actor(path, {'anim': path + '-Anim'})]
            self.__preload_models(models, callback, model, curr_t)
        else:
            eng.base.loader.loadModel(path, callback=
                lambda model: self.__preload_models(models, callback, model, curr_t))

    def __process_models(self, models):
        for model in models:
            model_name = model.getName().split('.')[0][5:]
            if model_name.endswith('Anim'):
                path = self.mdt.path + '/' + model_name
                self.__actors += [Actor(path, {'anim': path + '-Anim'})]
                self.__actors[-1].loop('anim')
                self.__actors[-1].reparent_to(model)
            else:
                self.__process_static(model)
        self.flattening()

    def __process_static(self, model):
        model_name = model.getName().split('.')[0][5:]
        if model_name not in self.__flat_roots:
            nstr = lambda i: '%s_%s' % (model_name, str(i))
            flat_roots = [self.model.attachNewNode(nstr(i)) for i in range(4)]
            self.__flat_roots[model_name] = flat_roots
        path = self.mdt.path + '/' + model.getName().split('.')[0][5:]
        eng.base.loader.loadModel(path).reparent_to(model)
        left, right, top, bottom = self.mdt.phys.lrtb
        center_x, center_y = (left + right) / 2, (top + bottom) / 2
        pos_x, pos_y = model.get_pos()[0], model.get_pos()[1]
        if not game.options['development']['split_world']:
            model.reparentTo(self.__flat_roots[model_name][0])
        elif pos_x < center_x and pos_y < center_y:
            model.reparentTo(self.__flat_roots[model_name][0])
        elif pos_x >= center_x and pos_y < center_y:
            model.reparentTo(self.__flat_roots[model_name][1])
        elif pos_x < center_x and pos_y >= center_y:
            model.reparentTo(self.__flat_roots[model_name][2])
        else:
            model.reparentTo(self.__flat_roots[model_name][3])

    def flattening(self):
        eng.log_mgr.log('track flattening')
        self.__flat_models(eng.logic.flatlist(self.__flat_roots.values()))

    def __flat_models(self, models, model='', time=0, nodes=0):
        if model:
            str_tmpl = 'flattened model: %s (%s seconds, %s nodes)'
            d_t = round(globalClock.getFrameTime() - time, 2)
            eng.log_mgr.log(str_tmpl % (model, d_t, nodes))
        if models:
            self.__process_flat_models(models, self.end_loading)
        else:
            self.end_loading()

    def __process_flat_models(self, models, callback):
        curr_t = globalClock.getFrameTime()
        node = models[0]
        node.clearModelNodes()

        def process_flat(flatten_node, orig_node, model, time, nodes):
            flatten_node.reparent_to(orig_node.get_parent())
            orig_node.remove_node()  # remove 1.9.3
            self.__flat_models(models[1:], model, time, nodes)
        nname = node.get_name()
        self.notify('on_loading', _('flattening model: ') + nname)
        if self.submodels:
            loader.asyncFlattenStrong(
                node, callback=process_flat, inPlace=False,
                extraArgs=[node, nname, curr_t, len(node.get_children())])
        else:
            len_children = len(node.get_children())
            process_flat(node, NodePath(''), node, curr_t, len_children)

    def end_loading(self):
        self.model.prepareScene(eng.base.win.getGsg())
        Gfx.async_build(self)

    def __set_light(self):
        ambient_lgt = AmbientLight('ambient light')
        ambient_lgt.setColor((.7, .7, .55, 1))
        self.ambient_np = render.attachNewNode(ambient_lgt)
        render.setLight(self.ambient_np)

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
        eng.base.render.clearLight(self.ambient_np)
        eng.base.render.clearLight(self.spot_lgt)
        self.ambient_np.removeNode()
        self.spot_lgt.removeNode()
        self.__actors = self.__flat_roots = None
