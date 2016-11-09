from panda3d.bullet import BulletRigidBodyNode, BulletTriangleMesh, \
    BulletTriangleMeshShape, BulletGhostNode
from racing.game.gameobject import Phys


class _Phys(Phys):

    def __init__(self, mdt, track_path):
        self.corners = None
        self.rigid_bodies = []
        self.ghosts = []
        self.nodes = []
        self.track_path = track_path
        Phys.__init__(self, mdt)

    def sync_build(self):
        self.model = loader.loadModel(self.track_path + '/collision')

        self.__load(['Road', 'Offroad'], False, False)
        self.__load(['Wall'], True, False)
        self.__load(['Goal', 'Slow', 'Respawn'], True, True)
        self.set_corners()

        _waypoints = self.model.findAllMatches('**/Waypoints/Waypoint*')
        self.waypoints = {}
        for w_p in _waypoints:
            wpstr = '**/Waypoints/Waypoint'
            prevs = w_p.getTag('prev').split(',')
            lst_wp = [self.model.find(wpstr + idx) for idx in prevs]
            self.waypoints[w_p] = lst_wp

        models = ['Road', 'Offroad', 'Wall', 'Respawn', 'Slow', 'Goal']
        map(self.hide_models, ['**/%s*' % mod for mod in models])

    def hide_models(self, models):
        models = self.model.findAllMatches(models)
        map(lambda mod: mod.hide(), models)

    def get_start_pos(self, i):
        start_pos = (0, 0, 0)
        start_pos_hpr = (0, 0, 0)
        node_str = '**/Start' + str(i + 1)
        start_pos_node = self.model.find(node_str)
        if start_pos_node:
            start_pos = self.model.find(node_str).get_pos()
            start_pos_hpr = self.model.find(node_str).get_hpr()
        return start_pos, start_pos_hpr

    def __load(self, names, merged, ghost):
        for geom_name in names:
            eng.log_mgr.log('setting physics for: ' + geom_name)
            geoms = eng.phys.find_geoms(self.model, geom_name)
            if geoms:
                self.__process_meshes(geoms, geom_name, merged, ghost)

    def __process_meshes(self, geoms, geom_name, merged, ghost):
        meth = self.add_geoms_merged if merged else self.add_geoms_unmerged
        if not merged:
            for geom in geoms:
                self.__build_mesh(meth, geom, geom_name, ghost)
        else:
            self.__build_mesh(meth, geoms, geom_name, ghost)

    @staticmethod
    def add_geoms_merged(geoms, mesh, phys_model, geom_name):
        for geom in geoms:
            transf = geom.getTransform(phys_model)
            for _geom in [g.decompose() for g in geom.node().getGeoms()]:
                mesh.addGeom(_geom, transf)
        return geom_name

    @staticmethod
    def add_geoms_unmerged(geoms, mesh, phys_model, geom_name):
        for _geom in [g.decompose() for g in geoms.node().getGeoms()]:
            mesh.addGeom(_geom, geoms.getTransform(phys_model))
        return geoms.get_name()

    def __build_mesh(self, meth, geoms, geom_name, ghost):
        mesh = BulletTriangleMesh()
        name = meth(geoms, mesh, self.model, geom_name)
        shape = BulletTriangleMeshShape(mesh, dynamic=False)
        self.__build(shape, name, ghost)

    def __build(self, shape, geom_name, ghost):
        if ghost:
            ncls = BulletGhostNode
            meth = eng.phys.world_phys.attachGhost
            lst = self.ghosts
        else:
            ncls = BulletRigidBodyNode
            meth = eng.phys.world_phys.attachRigidBody
            lst = self.rigid_bodies
        nodepath = eng.gfx.world_np.attachNewNode(ncls(geom_name))
        self.nodes += [nodepath]
        nodepath.node().addShape(shape)
        meth(nodepath.node())
        lst += [nodepath.node()]
        nodepath.node().notifyCollisions(True)

    def set_corners(self):
        if not self.corners:
            corners = ['topleft', 'topright', 'bottomright', 'bottomleft']
            pmod = self.model
            self.corners = [pmod.find('**/Minimap' + crn) for crn in corners]
        return self.corners

    @property
    def lrtb(self):
        return self.corners[0].getX(), self.corners[1].getX(), \
            self.corners[0].getY(), self.corners[3].getY()

    def destroy(self):
        self.model.removeNode()
        map(lambda chl: chl.remove_node(), self.nodes)
        map(eng.phys.world_phys.remove_rigid_body, self.rigid_bodies)
        map(eng.phys.world_phys.remove_ghost, self.ghosts)
