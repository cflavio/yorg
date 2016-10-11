'''This module provides the physics of a car.'''
from panda3d.bullet import BulletVehicle, ZUp, BulletConvexHullShape
from panda3d.core import TransformState, LVecBase3f, LPoint3f
from racing.game.gameobject.gameobject import Phys
import yaml


class _Phys(Phys):
    '''This class models the physics component of a car.'''

    def __init__(self, mdt, path):
        Phys.__init__(self, mdt)
        self.__set_phys(path)

        def find_geoms(model, name):
            '''Finds the geoms with the given name.'''
            def sibling_names(node):
                '''Finds the sibling of a node.'''
                siblings = node.getParent().getChildren()
                return [child.getName() for child in siblings]

            named_geoms = [
                geom for geom in model.findAllMatches('**/+GeomNode')
                if any([s.startswith(name) for s in sibling_names(geom)])]
            in_vec = [name in named_geom.getName()
                      for named_geom in named_geoms]
            indexes = [i for i, el in enumerate(in_vec) if el]
            return [named_geoms[i] for i in indexes]

        chassis_shape = BulletConvexHullShape()
        capsule = loader.loadModel('cars/capsule')
        capsule.setScale(*self.collision_box_scale)
        capsule.flattenLight()
        for geom in find_geoms(capsule, 'Cube'):
            geom_geom = geom.node().getGeom(0)
            transf = geom.getTransform()
            chassis_shape.addGeom(geom_geom, transf)

        transform_state = TransformState.makePos(
            LVecBase3f(*self.collision_box_pos))
        mdt.gfx.nodepath.node().addShape(chassis_shape, transform_state)
        mdt.gfx.nodepath.node().setMass(self.mass)
        mdt.gfx.nodepath.node().setDeactivationEnabled(False)

        eng.phys.world_phys.attachRigidBody(mdt.gfx.nodepath.node())
        eng.phys.collision_objs += [mdt.gfx.nodepath.node()]

        self.vehicle = BulletVehicle(eng.phys.world_phys,
                                     mdt.gfx.nodepath.node())
        self.vehicle.setCoordinateSystem(ZUp)
        self.vehicle.setPitchControl(self.pitch_control)
        tuning = self.vehicle.getTuning()
        tuning.setSuspensionCompression(self.suspension_compression)
        tuning.setSuspensionDamping(self.suspension_damping)

        eng.phys.world_phys.attachVehicle(self.vehicle)

        wheels_info = [
            (self.wheel_fr_pos, True, mdt.gfx.front_right_wheel_np,
             self.wheel_fr_radius),
            (self.wheel_fl_pos, True, mdt.gfx.front_left_wheel_np,
             self.wheel_fl_radius),
            (self.wheel_rr_pos, False, mdt.gfx.rear_right_wheel_np,
             self.wheel_rr_radius),
            (self.wheel_rl_pos, False, mdt.gfx.rear_left_wheel_np,
             self.wheel_rl_radius)]
        map(lambda (pos, front, nodepath, radius):
            self.__add_wheel(pos, front, nodepath.node(), radius),
            wheels_info)
        self.curr_max_speed = self.max_speed
        #mdt.gfx.nodepath.node().setCcdMotionThreshold(1e-7)
        #mdt.gfx.nodepath.node().setCcdSweptSphereRadius(3.50)
        #self.vehicle.get_chassis().setCcdMotionThreshold(.01)
        #self.vehicle.get_chassis().setCcdSweptSphereRadius(.2)

    def __set_phys(self, path):
        '''Sets the physics.'''
        with open('assets/models/%s/phys.yml' % path) as phys_file:
            conf = yaml.load(phys_file)
        fields = [
            'collision_box_shape', 'collision_box_pos', 'collision_box_scale',
            'wheel_fr_pos', 'wheel_fr_radius', 'wheel_fl_pos',
            'wheel_fl_radius', 'wheel_rr_pos', 'wheel_rr_radius',
            'wheel_rl_pos', 'wheel_rl_radius', 'max_speed', 'mass',
            'steering_min_speed', 'steering_max_speed', 'steering_clamp',
            'steering_inc', 'steering_dec', 'engine_acc_frc', 'engine_dec_frc',
            'brake_frc', 'eng_brk_frc', 'pitch_control',
            'suspension_compression', 'suspension_damping',
            'max_suspension_force', 'max_suspension_travel_cm', 'skid_info',
            'suspension_stiffness', 'wheels_damping_relaxation',
            'wheels_damping_compression', 'friction_slip', 'roll_influence']
        map(lambda field: setattr(self, field, conf[field]), fields)

    def __add_wheel(self, pos, front, node, radius):
        '''This method adds a wheel to the car.'''
        wheel = self.vehicle.createWheel()
        wheel.setNode(node)
        wheel.setChassisConnectionPointCs(LPoint3f(*pos))
        wheel.setFrontWheel(front)
        wheel.setWheelDirectionCs((0, 0, -1))
        wheel.setWheelAxleCs((1, 0, 0))
        wheel.setWheelRadius(radius)
        wheel.setSuspensionStiffness(self.suspension_stiffness)
        wheel.setWheelsDampingRelaxation(self.wheels_damping_relaxation)
        wheel.setWheelsDampingCompression(self.wheels_damping_compression)
        wheel.setFrictionSlip(self.friction_slip)
        wheel.setRollInfluence(self.roll_influence)
        wheel.setMaxSuspensionForce(self.max_suspension_force)
        wheel.setMaxSuspensionTravelCm(self.max_suspension_travel_cm)
        wheel.setSkidInfo(self.skid_info)

    @property
    def is_flying(self):
        '''Is the car flying?'''
        rays = [wheel.getRaycastInfo() for wheel in self.vehicle.get_wheels()]
        return not any(ray.isInContact() for ray in rays)

    @property
    def speed(self):
        '''The current speed.'''
        return self.vehicle.getCurrentSpeedKmHour()

    @property
    def speed_ratio(self):
        '''The current speed ratio.'''
        is_race = game.track.fsm.getCurrentOrNextState() == 'Race'
        return min(1.0, self.speed / self.max_speed) if is_race else 0

    def set_forces(self, eng_frc, brake_frc, steering):
        '''This callback method is invoked on each frame.'''
        self.vehicle.setSteeringValue(steering, 0)
        self.vehicle.setSteeringValue(steering, 1)
        self.vehicle.applyEngineForce(eng_frc, 2)
        self.vehicle.applyEngineForce(eng_frc, 3)
        self.vehicle.setBrake(brake_frc, 2)
        self.vehicle.setBrake(brake_frc, 3)

    @staticmethod
    def ground_name(wheel):
        '''The name of the ground under the wheel.'''
        contact_pos = wheel.get_raycast_info().getContactPointWs()
        result = eng.phys.world_phys.rayTestClosest(
            (contact_pos.x, contact_pos.y, contact_pos.z + .1),
            (contact_pos.x, contact_pos.y, contact_pos.z - .1))
        ground = result.get_node()
        return ground.get_name() if ground else ''

    @property
    def ground_names(self):
        '''The names of the grounds under the wheels.'''
        return [self.ground_name(wheel) for wheel in self.vehicle.get_wheels()]

    def update_terrain(self):
        '''Update physics settings of the car depending of the terrain.'''
        speeds = []
        frictions = []
        for wheel in self.vehicle.get_wheels():
            ground_name = self.ground_name(wheel)
            if ground_name:
                gfx_node = game.track.gfx.phys_model.find('**/' + ground_name)
                try:
                    speeds += [float(gfx_node.get_tag('speed'))]
                    frictions += [float(gfx_node.get_tag('friction'))]
                except ValueError:
                    pass
        if speeds:
            avg_speed = sum(speeds) / len(speeds)
        else:
            avg_speed = 1.0
        if frictions:
            avg_friction = sum(frictions) / len(frictions)
        else:
            avg_friction = 1.0
        self.curr_max_speed = self.max_speed * avg_speed
        for wheel in self.vehicle.get_wheels():
            wheel.setFrictionSlip(self.friction_slip * avg_friction)
