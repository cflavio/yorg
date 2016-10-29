from panda3d.bullet import BulletRigidBodyNode, BulletTriangleMesh, \
    BulletTriangleMeshShape, BulletGhostNode
from racing.game.gameobject import Phys


class MergedBuilder:

    def add_geoms(self, geoms, mesh, phys_model, geom_name):
        for geom in geoms:
            transf = geom.getTransform(phys_model)
            for _geom in [g.decompose() for g in geom.node().getGeoms()]:
                mesh.addGeom(_geom, transf)
        return geom_name


class UnmergedBuilder:

    def add_geoms(self, geoms, mesh, phys_model, geom_name):
        for _geom in [g.decompose() for g in geoms.node().getGeoms()]:
            mesh.addGeom(_geom, geoms.getTransform(phys_model))
        return geoms.get_name()


class _Phys(Phys):

    def __init__(self, mdt):
        Phys.__init__(self, mdt)
        self.corners = None
        self.rigid_bodies = []
        self.ghosts = []
        self.nodes = []
        self.__load(['Road', 'Offroad'], False, False)
        self.__load(['Wall'], True, False)
        self.__load(['Goal', 'Slow', 'Respawn'], True, True)
        self.set_corners()

    def __build(self, geom, shape, geom_name, ghost):
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

    def __load(self, names, merged, ghost):
        for geom_name in names:
            eng.log_mgr.log('setting physics for: ' + geom_name)
            geoms = eng.phys.find_geoms(self.mdt.gfx.phys_model, geom_name)
            if geoms:
                self.__process_meshes(geoms, geom_name, merged, ghost)

    def __build_mesh(self, geombuilder, geoms, geom_name, ghost):
        mesh = BulletTriangleMesh()
        name = geombuilder.add_geoms(geoms, mesh, self.mdt.gfx.phys_model, geom_name)
        shape = BulletTriangleMeshShape(mesh, dynamic=False)
        self.__build(geoms, shape, name, ghost)

    def __process_meshes(self, geoms, geom_name, merged, ghost):
        geombuilder = (MergedBuilder if merged else UnmergedBuilder)()
        if not merged:
            for geom in geoms:
                self.__build_mesh(geombuilder, geom, geom_name, ghost)
        else:
            self.__build_mesh(geombuilder, geoms, geom_name, ghost)

    def set_corners(self):
        if not self.corners:
            corners = ['topleft', 'topright', 'bottomright', 'bottomleft']
            self.corners = [self.mdt.gfx.phys_model.find('**/Minimap' + crn) for crn in corners]
        return self.corners

    @property
    def lrtb(self):
        return self.corners[0].getX(), self.corners[1].getX(), \
            self.corners[0].getY(), self.corners[3].getY()

    def destroy(self):
        map(lambda chl: chl.remove_node(), self.nodes)
        map(eng.phys.world_phys.remove_rigid_body, self.rigid_bodies)
        map(eng.phys.world_phys.remove_ghost, self.ghosts)
