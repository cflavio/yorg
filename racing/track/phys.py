'''This module provides physics for tracks.'''
from panda3d.bullet import BulletRigidBodyNode, BulletTriangleMesh, \
    BulletTriangleMeshShape, BulletGhostNode
from racing.game.gameobject.gameobject import Phys


class _Phys(Phys):
    '''This class models the physics component of a track.'''

    def __init__(self, mdt):
        Phys.__init__(self, mdt)

        for geom_name in ['Road', 'Offroad']:
            eng.log_mgr.log('setting physics for: ' + geom_name)
            geoms = self.__find_geoms(geom_name)
            if geoms:
                for geom in geoms:
                    self.__process_road(geom)

        for geom_name in ['Wall']:
            eng.log_mgr.log('setting physics for: ' + geom_name)
            geoms = self.__find_geoms(geom_name)
            if geoms:
                self.__process_wall(geoms, geom_name)

        for geom_name in ['Goal', 'Slow', 'Respawn']:
            eng.log_mgr.log('setting physics for: ' + geom_name)
            geoms = self.__find_geoms(geom_name)
            if geoms:
                self.__process_ghost(geoms, geom_name)

    def __find_geoms(self, name):
        '''Finds geoms with given name.'''
        # the list of geoms which have siblings named 'name'
        geoms = self.mdt.gfx.phys_model.findAllMatches('**/+GeomNode')
        is_nm = lambda geom: geom.getName().startswith(name)
        named_geoms = [geom for geom in geoms if is_nm(geom)]
        in_vec = [name in named_geom.getName() for named_geom in named_geoms]
        indexes = [i for i, el in enumerate(in_vec) if el]
        return [named_geoms[i] for i in indexes]

    def __process_road(self, geom):
        '''Processes roads.'''
        # we can't manage speed and friction if we merge meshes
        mesh = BulletTriangleMesh()
        for _geom in [g.decompose() for g in geom.node().getGeoms()]:
            mesh.addGeom(_geom, geom.getTransform(self.mdt.gfx.phys_model))
        shape = BulletTriangleMeshShape(mesh, dynamic=False)
        wrl = eng.gfx.world_np
        nodepath = wrl.attachNewNode(BulletRigidBodyNode(geom.get_name()))
        nodepath.node().addShape(shape)
        eng.phys.world_phys.attachRigidBody(nodepath.node())
        nodepath.node().notifyCollisions(True)

    def __process_wall(self, geoms, geom_name):
        '''Processes walls.'''
        mesh = BulletTriangleMesh()
        for geom in geoms:
            transf = geom.getTransform(self.mdt.gfx.phys_model)
            for _geom in [g.decompose() for g in geom.node().getGeoms()]:
                mesh.addGeom(_geom, transf)
        shape = BulletTriangleMeshShape(mesh, dynamic=False)
        wrl = eng.gfx.world_np
        nodepath = wrl.attachNewNode(BulletRigidBodyNode(geom_name))
        nodepath.node().addShape(shape)
        eng.phys.world_phys.attachRigidBody(nodepath.node())
        nodepath.node().notifyCollisions(True)

    def __process_ghost(self, geoms, geom_name):
        '''Processes ghosts.'''
        mesh = BulletTriangleMesh()
        for geom in geoms:
            transf = geom.getTransform(self.mdt.gfx.phys_model)
            for geom in [g.decompose() for g in geom.node().getGeoms()]:
                mesh.addGeom(geom, transf)
        shape = BulletTriangleMeshShape(mesh, dynamic=False)
        ghost = BulletGhostNode(geom_name)
        ghost.addShape(shape)
        ghost_np = eng.gfx.world_np.attachNewNode(ghost)
        eng.phys.world_phys.attachGhost(ghost)
        ghost_np.node().notifyCollisions(True)

    def destroy(self):
        eng.phys.stop()
