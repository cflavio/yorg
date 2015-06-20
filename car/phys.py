from panda3d.bullet import BulletBoxShape, BulletVehicle, ZUp
from panda3d.core import TransformState
from ya2.gameobject import Phys


class _Phys(Phys):
    '''This class models the physics component of a car.'''

    collision_box_shape = (.8, 1.4, .5)  # meters
    collision_box_pos = (0, 0, .5)  # meters
    wheel_fr_pos = (.75, 1.05, .4)  # meters
    wheel_fr_radius = .3  # meters
    wheel_fl_pos = (-.75, 1.05, .4)  # meters
    wheel_fl_radius = .3  # meters
    wheel_rr_pos = (.75, -.8, .4)  # meters
    wheel_rr_radius = .35  # meters
    wheel_rl_pos = (-.75, -.8, .4)  # meters
    wheel_rl_radius = .35  # meters
    max_speed = 90.0  # Km/h
    mass = 900  # kilograms
    steering_min_speed = 40  # degrees
    steering_max_speed = 10  # degrees
    steering_clamp = 40  # degrees
    steering_inc = 120  # degrees per second
    steering_dec = 120  # degrees per second
    engine_acc_frc = 5000
    engine_dec_frc = -2000
    brake_frc = 100
    pitch_control = 0  # default 0
    suspension_compression = 1  # default .83; should be lower than damping
    suspension_damping = .5  # default .88; should be greater than compression
    max_suspension_force = 8000  # default 6000
    max_suspension_travel_cm = 700  # default 500
    skid_info = 1  # default 1
    suspension_stiffness = 20  # default 5.88; f1 car == 200
    wheels_damping_relaxation = 2  # overwrites suspension_damping
    wheels_damping_compression = 4  # overwrites suspension_compression
    friction_slip = 3.5  # default 10.5
    roll_influence = .25  # default .1

    def __init__(self, mdt):
        Phys.__init__(self, mdt)
        chassis_shape = BulletBoxShape(self.collision_box_shape)
        transform_state = TransformState.makePos(self.collision_box_pos)
        mdt.gfx.nodepath.node().addShape(chassis_shape, transform_state)
        mdt.gfx.nodepath.node().setMass(self.mass)
        mdt.gfx.nodepath.node().setDeactivationEnabled(False)
        eng.world_phys.attachRigidBody(mdt.gfx.nodepath.node())

        self.vehicle = BulletVehicle(eng.world_phys, mdt.gfx.nodepath.node())
        self.vehicle.setCoordinateSystem(ZUp)
        self.vehicle.setPitchControl(self.pitch_control)
        tuning = self.vehicle.getTuning()
        tuning.setSuspensionCompression(self.suspension_compression)
        tuning.setSuspensionDamping(self.suspension_damping)

        eng.world_phys.attachVehicle(self.vehicle)

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

        #mdt.gfx.nodepath.node().setCcdMotionThreshold(1e-7)
        #mdt.gfx.nodepath.node().setCcdSweptSphereRadius(3.50)

    def __add_wheel(self, pos, front, node, radius):
        '''This method adds a wheel to the car.'''
        wheel = self.vehicle.createWheel()
        wheel.setNode(node)
        wheel.setChassisConnectionPointCs(pos)
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
    def speed(self):
        return self.vehicle.getCurrentSpeedKmHour()

    def set_forces(self, eng_frc, brake_frc, steering):
        '''This callback method is invoked on each frame.'''
        self.vehicle.setSteeringValue(steering, 0)
        self.vehicle.setSteeringValue(steering, 1)
        self.vehicle.applyEngineForce(eng_frc, 2)
        self.vehicle.applyEngineForce(eng_frc, 3)
        self.vehicle.setBrake(brake_frc, 2)
        self.vehicle.setBrake(brake_frc, 3)

    def destroy(self):
        '''The destroyer.'''
        self.vehicle.destroy()
