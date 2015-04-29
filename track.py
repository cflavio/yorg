''''In this module we define the track class.'''
from abc import ABCMeta
from direct.gui.OnscreenText import OnscreenText
from panda3d.bullet import BulletPlaneShape, BulletRigidBodyNode,\
    BulletTriangleMesh, BulletTriangleMeshShape, BulletGhostNode
from panda3d.core import BitMask32, AmbientLight, DirectionalLight, TextNode,\
    Spotlight
from ya2.gameobject import GameObjectMdt, Gfx, Gui, Phys


class _Phys(Phys):
    '''This class models the physics component of a track.'''

    def __init__(self, mdt):
        Phys.__init__(self, mdt)

        def find_geom(name):
            def sibling_names(node):
                siblings = node.getParent().getChildren()
                return [child.getName() for child in siblings]

            # the list of geoms which have siblings named 'name'
            named_geoms = [
                geom for geom in mdt.gfx.model.findAllMatches('**/+GeomNode')
                if any([name in [s for s in sibling_names(geom)]])]
            return named_geoms[0].node().getGeom(0)

        for geom_name in ['Road', 'Wall']:
            geom = find_geom(geom_name)
            mesh = BulletTriangleMesh()
            mesh.addGeom(geom)
            shape = BulletTriangleMeshShape(mesh, dynamic=False)
            np = eng.world_np.attachNewNode(BulletRigidBodyNode(geom_name))
            np.node().addShape(shape)
            eng.world_phys.attachRigidBody(np.node())
            np.node().notifyCollisions(True)

        for geom_name in ['Goal']:
            geom = find_geom(geom_name)
            mesh = BulletTriangleMesh()
            mesh.addGeom(geom)
            shape = BulletTriangleMeshShape(mesh, dynamic=False)
            ghost = BulletGhostNode(geom_name)
            ghost.addShape(shape)
            ghostNP = eng.world_np.attachNewNode(ghost)
            eng.world_phys.attachGhost(ghost)
            ghostNP.node().notifyCollisions(True)

        for geom_name in ['Slow']:
            geom = find_geom(geom_name)
            mesh = BulletTriangleMesh()
            mesh.addGeom(geom)
            shape = BulletTriangleMeshShape(mesh, dynamic=False)
            ghost = BulletGhostNode(geom_name)
            ghost.addShape(shape)
            ghostNP = eng.world_np.attachNewNode(ghost)
            eng.world_phys.attachGhost(ghost)
            ghostNP.node().notifyCollisions(True)


class _Gui(Gui):
    '''This class models the GUI component of a track.'''

    def __init__(self, mdt):
        Gui.__init__(self, mdt)
        self.__debug_txt = OnscreenText(
            _('F12: toggle debug'), pos=(-.1, .1), scale=0.07,
            parent=eng.a2dBottomRight, align=TextNode.ARight,
            font=eng.font_mgr.load_font('assets/fonts/zekton rg.ttf'))

    def destroy(self):
        Gui.destroy(self)
        self.__debug_txt.destroy()


class _Gfx(Gfx):
    '''This class models the graphics component of a track.'''

    def __init__(self, mdt):
        Gfx.__init__(self, mdt)
        self.__set_model()
        self.__set_light()
        self.__set_camera()

    def __set_model(self):
        self.model = loader.loadModel("track/track")
        self.model.reparentTo(render)
        self.model.hide(BitMask32.bit(0))
        self.model.find('**/Slow').hide()
        waypoints = self.model.findAllMatches('**/Waypoint*')
        for waypoint in waypoints:
            print waypoint, waypoint.getPos()

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

        spot_lgt = render.attachNewNode(Spotlight('Spot'))
        spot_lgt.node().setScene(render)
        spot_lgt.node().setShadowCaster(True, 1024, 1024)
        spot_lgt.node().getLens().setFov(40)
        spot_lgt.node().getLens().setNearFar(20, 200)
        spot_lgt.node().setCameraMask(BitMask32.bit(0))
        spot_lgt.setPos(50, -80, 80)
        spot_lgt.lookAt(0, 0, 0)
        render.setLight(spot_lgt)
        render.setShaderAuto()

    def __set_camera(self):
        eng.cam.setPos(0, -40, 15)
        eng.cam.lookAt(0, 0, 0)

    def destroy(self):
        '''The destroyer.'''
        self.nodepath.removeNode()


class Track(GameObjectMdt):
    '''The Track class.'''
    __metaclass__ = ABCMeta
    gfx_cls = _Gfx
    phys_cls = _Phys
    gui_cls = _Gui
