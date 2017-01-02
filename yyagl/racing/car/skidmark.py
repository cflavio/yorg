from panda3d.core import GeomVertexData, GeomVertexWriter, GeomVertexFormat,\
    Geom, GeomTriangles, GeomNode, GeomVertexReader, Mat4, Material,\
    OmniBoundingVolume


class Skidmark:

    def __init__(self, car, whl):
        self.car = car
        self.whl = whl
        self.vdata = GeomVertexData('skid', GeomVertexFormat.getV3(), Geom.UHDynamic)
        self.vdata.setNumRows(1)
        self.vertex = GeomVertexWriter(self.vdata, 'vertex')
        self.width = .12
        self.prim = GeomTriangles(Geom.UHStatic)
        self.cnt = 1
        self.last_pos = self.car.gfx.wheels[self.whl].get_pos(render)
        geom = Geom(self.vdata)
        geom.addPrimitive(self.prim)
        node = GeomNode('gnode')
        node.addGeom(geom)
        nodePath = render.attachNewNode(node)
        mat = Material()
        mat.setAmbient((.35, .35, .35, .5))
        mat.setDiffuse((.35, .35, .35, .5))
        mat.setSpecular((.35, .35, .35, .5))
        mat.setShininess(12.5)
        nodePath.set_material(mat, 1)
        nodePath.node().setBounds(OmniBoundingVolume())
        self.add_vertices()

    def add_vertices(self):
        base_pos = self.last_pos + (0, 0, -self.car.phys.vehicle.getWheels()[0].getWheelRadius() + .05)
        rot_mat = Mat4()
        rot_mat.setRotateMat(self.car.gfx.nodepath.get_h(), (0, 0, 1))
        self.vertex.addData3f(base_pos + rot_mat.xformVec((-self.width, 0, 0)))
        self.vertex.addData3f(base_pos + rot_mat.xformVec((self.width, 0, 0)))
        if self.cnt >= 3:
            self.prim.addVertices(self.cnt - 3, self.cnt, self.cnt - 1)
            self.prim.addVertices(self.cnt - 3, self.cnt -2, self.cnt)
        self.cnt += 2

    def update(self):
        if not hasattr(self, 'vdata'):
            return
        fr_pos = self.car.gfx.wheels[self.whl].get_pos(render)
        if (fr_pos - self.last_pos).length() < .2:
            return
        self.last_pos = fr_pos
        self.add_vertices()

    def destroy(self):
        self.car = None
