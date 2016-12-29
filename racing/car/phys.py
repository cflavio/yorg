from panda3d.bullet import BulletVehicle, ZUp, BulletConvexHullShape
from panda3d.core import TransformState, LVecBase3f, LPoint3f
from racing.game.gameobject import Phys
import yaml


class CarPhys(Phys):

    def __init__(self, mdt, name, track_phys):
        Phys.__init__(self, mdt)
        self.pnode = None
        self.vehicle = None
        self.curr_speed_factor = 1.0
        self.__finds = {}
        self.__track_phys = track_phys
        self._load_phys(name)
        self.__set_collision(name)
        self.__set_phys_node()
        self.__set_vehicle()
        self.__set_wheels()

    def _load_phys(self, name):
        with open('assets/models/%s/phys.yml' % name) as phys_file:
            conf = yaml.load(phys_file)
        map(lambda field: setattr(self, field, conf[field]), conf.keys())

    def __set_collision(self, name):
        self.capsule = loader.loadModel('%s/capsule' % name)
        chassis_shape = BulletConvexHullShape()
        for geom in eng.phys.find_geoms(self.capsule, 'Capsule'):
            chassis_shape.addGeom(geom.node().getGeom(0), geom.getTransform())
        self.mdt.gfx.nodepath.node().addShape(chassis_shape)

    def __set_phys_node(self):
        self.pnode = self.mdt.gfx.nodepath.node()
        self.pnode.setMass(self.mass)
        self.pnode.setDeactivationEnabled(False)
        eng.phys.world_phys.attachRigidBody(self.pnode)
        eng.phys.collision_objs += [self.pnode]

    def __set_vehicle(self):
        self.vehicle = BulletVehicle(eng.phys.world_phys, self.pnode)
        self.vehicle.setCoordinateSystem(ZUp)
        self.vehicle.setPitchControl(self.pitch_control)
        tuning = self.vehicle.getTuning()
        tuning.setSuspensionCompression(self.suspension_compression)
        tuning.setSuspensionDamping(self.suspension_damping)
        eng.phys.world_phys.attachVehicle(self.vehicle)

    def __set_wheels(self):
        fwheel_bounds = self.mdt.gfx.wheels['fr'].get_tight_bounds()
        f_radius = (fwheel_bounds[1][2] - fwheel_bounds[0][2]) / 2.0  + .01
        self.wheel_fr_radius = self.wheel_fl_radius = f_radius
        rwheel_bounds = self.mdt.gfx.wheels['rr'].get_tight_bounds()
        r_radius = (rwheel_bounds[1][2] - rwheel_bounds[0][2]) / 2.0 + .01
        self.wheel_rr_radius = self.wheel_rl_radius = r_radius
        ffr = self.capsule.find('**/EmptyWheelFront')
        ffl = self.capsule.find('**/EmptyWheelFront.001')
        rrr = self.capsule.find('**/EmptyWheelRear')
        rrl = self.capsule.find('**/EmptyWheelRear.001')
        fr_node = ffr if ffr else self.capsule.find('**/EmptyWheel')
        fl_node = ffl if ffl else self.capsule.find('**/EmptyWheel.001')
        rr_node = rrr if rrr else self.capsule.find('**/EmptyWheel.002')
        rl_node = rrl if rrl else self.capsule.find('**/EmptyWheel.003')
        self.wheel_fr_pos = fr_node.get_pos() + (0, 0, f_radius)
        self.wheel_fl_pos = fl_node.get_pos() + (0, 0, f_radius)
        self.wheel_rr_pos = rr_node.get_pos() + (0, 0, r_radius)
        self.wheel_rl_pos = rl_node.get_pos() + (0, 0, r_radius)
        frw = self.mdt.gfx.wheels['fr']
        flw = self.mdt.gfx.wheels['fl']
        rrw = self.mdt.gfx.wheels['rr']
        rlw = self.mdt.gfx.wheels['rl']
        wheels_info = [
            (self.wheel_fr_pos, True, frw, self.wheel_fr_radius),
            (self.wheel_fl_pos, True, flw, self.wheel_fl_radius),
            (self.wheel_rr_pos, False, rrw, self.wheel_rr_radius),
            (self.wheel_rl_pos, False, rlw, self.wheel_rl_radius)]
        #TODO: change this to a for
        map(lambda (pos, front, nodepath, radius):
            self.__add_wheel(pos, front, nodepath.node(), radius),
            wheels_info)

    def __add_wheel(self, pos, front, node, radius):
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
        rays = [wheel.getRaycastInfo() for wheel in self.vehicle.get_wheels()]
        return not any(ray.isInContact() for ray in rays)

    @property
    def speed(self):
        return self.vehicle.getCurrentSpeedKmHour()

    @property
    def speed_ratio(self):
        return max(0, min(1.0, self.speed / self.max_speed))

    def set_forces(self, eng_frc, brake_frc, steering):
        self.vehicle.setSteeringValue(steering, 0)
        self.vehicle.setSteeringValue(steering, 1)
        self.vehicle.applyEngineForce(eng_frc, 2)
        self.vehicle.applyEngineForce(eng_frc, 3)
        self.vehicle.setBrake(brake_frc, 2)
        self.vehicle.setBrake(brake_frc, 3)

    def update_car_props(self):
        speeds = []
        for wheel in self.vehicle.get_wheels():
            ground_name = self.ground_name(wheel)
            if not ground_name:
                continue
            if ground_name not in self.__finds:
                ground = self.__track_phys.find('**/' + ground_name)
                self.__finds[ground_name] = ground
            gfx_node = self.__finds[ground_name]
            if gfx_node.has_tag('speed'):
                speeds += [float(gfx_node.get_tag('speed'))]
            if gfx_node.has_tag('friction'):
                fric = float(gfx_node.get_tag('friction'))
                wheel.setFrictionSlip(self.friction_slip * fric)
        self.curr_speed_factor = (sum(speeds) / len(speeds)) if speeds else 1.0

    @property
    def ground_names(self):
        return map(self.ground_name, self.vehicle.get_wheels())

    @staticmethod
    def ground_name(wheel):
        contact_pos = wheel.get_raycast_info().getContactPointWs()
        top = contact_pos + (0, 0, .1)
        bottom = contact_pos + (0, 0, -.1)
        result = eng.phys.world_phys.rayTestClosest(top, bottom)
        ground = result.get_node()
        return ground.get_name() if ground else ''

    def apply_damage(self):
        self.max_speed *= .95
        self.friction_slip *= .95
        self.roll_influence *= .95
        map(lambda whl: whl.setFrictionSlip(self.friction_slip), self.vehicle.get_wheels())
        map(lambda whl: whl.setRollInfluence(self.roll_influence), self.vehicle.get_wheels())
        eng.log_mgr.log('speed: ' + str(round(self.max_speed, 2)))
        eng.log_mgr.log('friction: ' + str(round(self.friction_slip, 2)))
        eng.log_mgr.log('roll: ' + str(round(self.roll_influence, 2)))

    def destroy(self):
        eng.phys.world_phys.remove_vehicle(self.vehicle)
        self.pnode = self.vehicle = self.__finds = self.__track_phys = \
            self.capsule = None
        Phys.destroy(self)


class CarPlayerPhys(CarPhys):

    def _load_phys(self, name):
        with open('assets/models/%s/phys.yml' % name) as phys_file:
            conf = yaml.load(phys_file)
        new_speed = conf['max_speed'] * (1 + .1 * game.logic.season.logic.tuning.logic.tuning['engine'])
        conf['max_speed'] = new_speed
        new_fric = conf['friction_slip'] * (1 + .1 * game.logic.season.logic.tuning.logic.tuning['tires'])
        conf['friction_slip'] = new_fric
        new_roll = conf['roll_influence'] * (1 + .1 * game.logic.season.logic.tuning.logic.tuning['suspensions'])
        conf['roll_influence'] = new_roll
        eng.log_mgr.log('speed: ' + str(round(new_speed, 2)))
        eng.log_mgr.log('friction: ' + str(round(new_fric, 2)))
        eng.log_mgr.log('roll: ' + str(round(new_roll, 2)))
        map(lambda field: setattr(self, field, conf[field]), conf.keys())