'''This module provides physics for tracks.'''
from panda3d.bullet import BulletRigidBodyNode, BulletTriangleMesh, \
    BulletTriangleMeshShape, BulletGhostNode
from racing.game.gameobject.gameobject import Phys


class _Phys(Phys):
    '''This class models the physics component of a track.'''

    def __init__(self, mdt):
        Phys.__init__(self, mdt)

        def find_geoms(name):
            '''Finds geoms with given name.'''
            # the list of geoms which have siblings named 'name'
            named_geoms = [
                geom
                for geom in mdt.gfx.phys_model.findAllMatches('**/+GeomNode')
                if geom.getName().startswith(name)]
            in_vec = [name in named_geom.getName() for
                      named_geom in named_geoms]
            indexes = [i for i, el in enumerate(in_vec) if el]
            return [named_geoms[i] for i in indexes]
        for geom_name in ['Road', 'Offroad']:
            eng.log_mgr.log('setting physics for: ' + geom_name)
            geoms = find_geoms(geom_name)
            if geoms:
                # we can't manage speed and friction if we merge meshes
                #mesh = BulletTriangleMesh()
                #for geom in geoms:
                #    eng.log_mgr.log('setting physics for: ' + geom.get_name())
                #    ts = geom.getTransform(mdt.gfx.phys_model)
                #    for _geom in [g.decompose()
                #                  for g in geom.node().getGeoms()]:
                #        mesh.addGeom(_geom, ts)
                #shape = BulletTriangleMeshShape(mesh, dynamic=False)
                # we can't manage speed and friction if we merge meshes
                #np = eng.world_np.attachNewNode(
                #    BulletRigidBodyNode(geom_name))
                #np.node().addShape(shape)
                #eng.world_phys.attachRigidBody(np.node())
                #np.node().notifyCollisions(True)
                for geom in geoms:
                    transf = geom.getTransform(mdt.gfx.phys_model)
                    mesh = BulletTriangleMesh()
                    for _geom in [g.decompose()
                                  for g in geom.node().getGeoms()]:
                        mesh.addGeom(_geom, transf)
                    shape = BulletTriangleMeshShape(mesh, dynamic=False)
                    nodepath = eng.gfx.world_np.attachNewNode(
                        BulletRigidBodyNode(geom.get_name()))
                    nodepath.node().addShape(shape)
                    eng.phys.world_phys.attachRigidBody(nodepath.node())
                    nodepath.node().notifyCollisions(True)

        for geom_name in ['Wall']:
            eng.log_mgr.log('setting physics for: ' + geom_name)
            geoms = find_geoms(geom_name)
            if geoms:
                mesh = BulletTriangleMesh()
                for geom in geoms:
                    transf = geom.getTransform(mdt.gfx.phys_model)
                    for _geom in [g.decompose()
                                  for g in geom.node().getGeoms()]:
                        mesh.addGeom(_geom, transf)
                shape = BulletTriangleMeshShape(mesh, dynamic=False)
                nodepath = eng.gfx.world_np.attachNewNode(
                    BulletRigidBodyNode(geom_name))
                nodepath.node().addShape(shape)
                eng.phys.world_phys.attachRigidBody(nodepath.node())
                nodepath.node().notifyCollisions(True)

        for geom_name in ['Goal']:
            eng.log_mgr.log('setting physics for: ' + geom_name)
            geoms = find_geoms(geom_name)
            if geoms:
                mesh = BulletTriangleMesh()
                for geom in geoms:
                    transf = geom.getTransform(mdt.gfx.phys_model)
                    for geom in [g.decompose()
                                 for g in geom.node().getGeoms()]:
                        mesh.addGeom(geom, transf)
                shape = BulletTriangleMeshShape(mesh, dynamic=False)
                ghost = BulletGhostNode(geom_name)
                ghost.addShape(shape)
                ghost_np = eng.gfx.world_np.attachNewNode(ghost)
                eng.phys.world_phys.attachGhost(ghost)
                ghost_np.node().notifyCollisions(True)

        for geom_name in ['Slow']:
            eng.log_mgr.log('setting physics for: ' + geom_name)
            geoms = find_geoms(geom_name)
            if geoms:
                mesh = BulletTriangleMesh()
                for geom in geoms:
                    transf = geom.getTransform(mdt.gfx.phys_model)
                    for geom in [g.decompose()
                                 for g in geom.node().getGeoms()]:
                        mesh.addGeom(geom, transf)
                shape = BulletTriangleMeshShape(mesh, dynamic=False)
                ghost = BulletGhostNode(geom_name)
                ghost.addShape(shape)
                ghost_np = eng.gfx.world_np.attachNewNode(ghost)
                eng.phys.world_phys.attachGhost(ghost)
                ghost_np.node().notifyCollisions(True)

        for geom_name in ['Respawn']:
            eng.log_mgr.log('setting physics for: ' + geom_name)
            geoms = find_geoms(geom_name)
            if geoms:
                mesh = BulletTriangleMesh()
                for geom in geoms:
                    transf = geom.getTransform(mdt.gfx.phys_model)
                    for geom in [g.decompose()
                                 for g in geom.node().getGeoms()]:
                        mesh.addGeom(geom, transf)
                shape = BulletTriangleMeshShape(mesh, dynamic=False)
                ghost = BulletGhostNode(geom_name)
                ghost.addShape(shape)
                ghost_np = eng.gfx.world_np.attachNewNode(ghost)
                eng.phys.world_phys.attachGhost(ghost)
                ghost_np.node().notifyCollisions(True)

    def destroy(self):
        eng.phys.stop()
