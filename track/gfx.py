from panda3d.core import AmbientLight, BitMask32, Spotlight
from direct.actor.Actor import Actor
from ya2.gameobject import Gfx


class _Gfx(Gfx):
    '''This class models the graphics component of a track.'''

    def __init__(self, mdt):
        Gfx.__init__(self, mdt)
        self.__set_model()
        self.__set_light()

    def __set_model(self):
        self.model = loader.loadModel("track/track")
        self.model.reparentTo(render)
        self.model.hide(BitMask32.bit(0))
        wp_idx = 0
        self.waypoints = []
        while self.model.find('**/Waypoint' + str(wp_idx)):
            self.waypoints += [self.model.find('**/Waypoint' + str(wp_idx))]
            wp_idx += 1
        road = self.model.find('**/Road')
        if road:
            road.hide()
        wall = self.model.find('**/Wall')
        if wall:
            wall.hide()
        slow_models = self.model.findAllMatches('**/Slow*')
        for model in slow_models:
            model.hide()
        goal = self.model.find('**/Goal')
        if goal:
            goal.hide()
        self.__load_empties()
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


    def __load_empties(self):
        empty_models = self.model.findAllMatches('**/Empty*')
        self.__actors = []
        self.__flat_roots = {}
        for model in empty_models:
            model_name = model.getName().split('.')[0][5:]
            if model_name.endswith('Anim'):
                self.__actors += [Actor('track/' + model_name, {
                    'anim': 'track/' + model_name + '-Anim'})]
                self.__actors[-1].loop('anim')
                self.__actors[-1].reparent_to(model)
            else:
                if model_name not in self.__flat_roots:
                    flat_root = self.model.attachNewNode(model_name)
                    self.__flat_roots[model_name] = flat_root
                child = eng.loader.loadModel('track/'+model.getName().split('.')[0][5:])
                child.reparent_to(model)
                model.reparentTo(self.__flat_roots[model_name])
        for node in self.__flat_roots.values():
            node.clearModelNodes()
            node.flattenStrong()

    def __set_light(self):
        eng.render.clearLight()

        ambient_lgt = AmbientLight('ambient light')
        ambient_lgt.setColor((.25, .25, .25, 1))
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
