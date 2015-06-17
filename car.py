'''In this module we define the Car classes.'''
from abc import ABCMeta
from direct.showbase.InputStateGlobal import inputState
from panda3d.bullet import BulletBoxShape, BulletVehicle, ZUp, \
    BulletRigidBodyNode
from panda3d.core import TransformState, AudioSound, TextNode

from ya2.gameobject import Event, GameObjectMdt, Gfx, Logic, Phys, Audio, Gui
from ya2 import gui
from direct.gui.DirectSlider import DirectSlider
from direct.gui.OnscreenText import OnscreenText


class _Phys(Phys):
    '''This class models the physics component of a car.'''

    collision_box_shape = (.6, 1.4, .5)  # meters
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


class _Audio(Audio):

    def __init__(self, mdt):
        Audio.__init__(self, mdt)
        self.engine_sfx = loader.loadSfx('assets/sfx/engine.ogg')
        self.brake_sfx = loader.loadSfx('assets/sfx/brake.ogg')
        self.crash_sfx = loader.loadSfx('assets/sfx/crash.ogg')
        map(lambda sfx: sfx.set_loop(True), [self.engine_sfx, self.brake_sfx, self.crash_sfx])
        self.engine_sfx.play()

    def update(self, input_dct):
        if input_dct['reverse'] and self.mdt.phys.speed > 50.0 and \
                self.brake_sfx.status() != AudioSound.PLAYING:
            self.brake_sfx.play()
        if not input_dct['reverse'] or self.mdt.phys.speed < 50.0:
            self.brake_sfx.stop()
        speed_ratio = self.mdt.phys.speed / self.mdt.phys.max_speed
        self.engine_sfx.set_volume(max(.25, abs(speed_ratio)))


class _Event(Event):
    '''This class manages the events of the Car class.'''

    def __init__(self, mdt):
        Event.__init__(self, mdt)
        label_events = [('forward', 'arrow_up'),
                        ('left', 'arrow_left'),
                        ('reverse', 'z'),
                        ('right', 'arrow_right')]
        map(lambda (lab, evt): inputState.watchWithModifiers(lab, evt),
            label_events)
        self.accept('bullet-contact-added', self.on_collision)
        self.accept('f11', self.mdt.gui.toggle)
        self.__last_wall_time = None
        self.__last_goal_time = None
        self.__last_slow_time = None

    def on_collision(self, node1, node2):
        if node2.getName() == 'Wall':
            self.__last_wall_time = globalClock.getFrameTime()
        if node2.getName() == 'Goal':
            self.__last_goal_time = globalClock.getFrameTime()
        if node2.getName() == 'Slow':
            self.__last_slow_time = globalClock.getFrameTime()

    def evt_OnFrame(self, evt):
        '''This callback method is invoked on each frame.'''
        input_dct = {
            'forward': inputState.isSet('forward'),
            'left': inputState.isSet('left'),
            'reverse': inputState.isSet('reverse'),
            'right': inputState.isSet('right')}
        self.mdt.logic.update(input_dct)
        self.mdt.audio.update(input_dct)
        if self.__last_wall_time and \
                globalClock.getFrameTime() - self.__last_wall_time > .05:
            self.__last_wall_time = None
            print 'wall'
        if self.__last_goal_time and \
                globalClock.getFrameTime() - self.__last_goal_time > .05:
            self.__last_goal_time = None
            print 'goal'
        if self.__last_slow_time and \
                globalClock.getFrameTime() - self.__last_slow_time > .05:
            self.__last_slow_time = None
            print 'slow'
        eng.camera.setPos(self.mdt.gfx.nodepath.getPos())


class _Gfx(Gfx):
    '''This class models the graphics component of a car.'''

    def __init__(self, mdt):
        Gfx.__init__(self, mdt)
        vehicle_node = BulletRigidBodyNode('Vehicle')
        self.nodepath = eng.world_np.attachNewNode(vehicle_node)

        self.chassis_np = eng.loader.loadModel('car/car')
        self.chassis_np.reparentTo(self.nodepath)
        self.chassis_np.setDepthOffset(-2)

        self.front_right_wheel_np = eng.loader.loadModel('car/frontwheel')
        self.front_right_wheel_np.reparentTo(eng.world_np)

        self.front_left_wheel_np = eng.loader.loadModel('car/frontwheel')
        self.front_left_wheel_np.reparentTo(eng.world_np)

        self.rear_right_wheel_np = eng.loader.loadModel('car/rearwheel')
        self.rear_right_wheel_np.reparentTo(eng.world_np)

        self.rear_left_wheel_np = eng.loader.loadModel('car/rearwheel')
        self.rear_left_wheel_np.reparentTo(eng.world_np)

    def destroy(self):
        '''The destroyer.'''
        meshes = [self.nodepath,
                  self.chassis_np,
                  self.front_right_wheel_np,
                  self.front_left_wheel_np,
                  self.rear_right_wheel_np,
                  self.rear_right_wheel_np]
        map(lambda mesh: mesh.destroy(), meshes)


class _Logic(Logic):
    '''This class manages the events of the Car class.'''

    def __init__(self, mdt):
        Logic.__init__(self, mdt)
        self.__steering = 0  # degrees

    def update(self, input_dct):
        '''This callback method is invoked on each frame.'''
        eng_frc = brake_frc = 0
        d_t = globalClock.getDt()
        steering_inc = d_t * self.mdt.phys.steering_inc
        steering_dec = d_t * self.mdt.phys.steering_dec

        speed_ratio = min(1.0, self.mdt.phys.speed / self.mdt.phys.max_speed)
        steering_range = self.mdt.phys.steering_min_speed - self.mdt.phys.steering_max_speed
        steering_clamp = self.mdt.phys.steering_min_speed - speed_ratio * steering_range

        if input_dct['forward']:
            eng_frc = self.mdt.phys.engine_acc_frc if self.mdt.phys.speed < self.mdt.phys.max_speed else 0
            brake_frc = 0

        if input_dct['reverse']:
            eng_frc = self.mdt.phys.engine_dec_frc if self.mdt.phys.speed < .05 else 0
            brake_frc = self.mdt.phys.brake_frc

        if input_dct['left']:
            self.__steering += steering_inc
            self.__steering = min(self.__steering, steering_clamp)

        if input_dct['right']:
            self.__steering -= steering_inc
            self.__steering = max(self.__steering, -steering_clamp)

        if not input_dct['left'] and not input_dct['right']:
            if abs(self.__steering) <= steering_dec:
                self.__steering = 0
            else:
                steering_sign = (-1 if self.__steering > 0 else 1)
                self.__steering += steering_sign * steering_dec

        self.mdt.phys.set_forces(eng_frc, brake_frc, self.__steering)
        self.mdt.gui.speed_txt.setText(
            _('Speed')+': '+str(round(self.mdt.phys.speed, 2)))

class CarParameter:

    def __init__(self, attr, init_val, pos, val_range, cb):
        self.__cb = cb
        self.__lab = OnscreenText(text=attr, pos=pos, scale=.04,
            align=TextNode.ARight, parent=eng.a2dTopLeft, fg=(1, 1, 1, 1))
        self.__slider = DirectSlider(
            pos=(pos[0]+.5, 0, pos[1]+.01), scale=.4, parent=eng.a2dTopLeft,
            value=init_val, range=val_range, command=self.__set_attr)
        self.__val = OnscreenText(
            pos=(pos[0]+1.0, pos[1]), scale=.04, align=TextNode.ALeft,
            parent=eng.a2dTopLeft, fg=(1, 1, 1, 1))
        self.toggle()

    def toggle(self):
        for wdg in [self.__slider, self.__lab, self.__val]:
            (wdg.show if wdg.isHidden() else wdg.hide)()

    def __set_attr(self):
        self.__cb(self.__slider['value'])
        self.__val.setText(str(round(self.__slider['value'], 2)))

    def destroy(self):
        map(lambda wdg: wdg.destroy(), [self.__slider, self.__lab, self.__val])


class _Gui(Gui):
    '''This class models the GUI component of a car.'''

    def __init__(self, mdt):
        Gui.__init__(self, mdt)
        self.__max_speed_par = CarParameter(
            'max_speed', self.mdt.phys.max_speed, (.5, -.04), (10.0, 200.0),
            lambda val: setattr(self.mdt.phys, 'max_speed', val))
        self.__mass_par = CarParameter(
            'mass', self.mdt.phys.mass, (.5, -.12), (100, 2000),
            self.mdt.gfx.nodepath.node().setMass)
        self.__steering_min_speed = CarParameter(
            'steering_min_speed', self.mdt.phys.steering_min_speed, (.5, -.2),
            (10.0, 100.0),
            lambda val: setattr(self.mdt.phys, 'steering_min_speed', val))
        self.__steering_max_speed = CarParameter(
            'steering_max_speed', self.mdt.phys.steering_max_speed, (.5, -.28),
            (1.0, 50.0),
            lambda val: setattr(self.mdt.phys, 'steering_max_speed', val))
        self.__steering_clamp = CarParameter(
            'steering_clamp', self.mdt.phys.steering_clamp, (.5, -.36),
            (1, 100),
            lambda val: setattr(self.mdt.phys, 'steering_clamp', val))
        self.__steering_inc = CarParameter(
            'steering_inc', self.mdt.phys.steering_inc, (.5, -.44), (1, 200),
            lambda val: setattr(self.mdt.phys, 'steering_inc', val))
        self.__steering_dec = CarParameter(
            'steering_dec', self.mdt.phys.steering_dec, (.5, -.52), (1, 200),
            lambda val: setattr(self.mdt.phys, 'steering_dec', val))
        self.__engine_acc_frc = CarParameter(
            'engine_acc_frc', self.mdt.phys.engine_acc_frc, (.5, -.6),
            (100, 10000),
            lambda val: setattr(self.mdt.phys, 'engine_acc_frc', val))
        self.__engine_dec_frc = CarParameter(
            'engine_dec_frc', self.mdt.phys.engine_dec_frc, (.5, -.68),
            (-10000, -100),
            lambda val: setattr(self.mdt.phys, 'engine_dec_frc', val))
        self.__brake_frc = CarParameter(
            'brake_frc', self.mdt.phys.brake_frc, (.5, -.76),
            (1, 1000),
            lambda val: setattr(self.mdt.phys, 'brake_frc', val))
        self.__pitch_control = CarParameter(
            'pitch_control', self.mdt.phys.pitch_control, (.5, -.84),
            (-10, 10), self.mdt.phys.vehicle.setPitchControl)
        self.__suspension_compression = CarParameter(
            'suspension_compression', self.mdt.phys.suspension_compression,
            (.5, -.92), (-1, 10),
            self.mdt.phys.vehicle.getTuning().setSuspensionCompression)
        self.__suspension_damping = CarParameter(
            'suspension_damping', self.mdt.phys.suspension_damping,
            (.5, -1.0), (-1, 10),
            self.mdt.phys.vehicle.getTuning().setSuspensionDamping)
        self.__max_suspension_force = CarParameter(
            'max_suspension_force', self.mdt.phys.max_suspension_force,
            (.5, -1.08), (1, 15000),
            lambda val: map(lambda whl: whl.setMaxSuspensionForce(val),
                            self.mdt.phys.vehicle.get_wheels()))
        self.__max_suspension_travel_cm = CarParameter(
            'max_suspension_travel_cm', self.mdt.phys.max_suspension_travel_cm,
            (.5, -1.16), (1, 2000),
            lambda val: map(lambda whl: whl.setMaxSuspensionTravelCm(val),
                            self.mdt.phys.vehicle.get_wheels()))
        self.__skid_info = CarParameter(
            'skid_info', self.mdt.phys.skid_info,
            (.5, -1.24), (-10, 10),
            lambda val: map(lambda whl: whl.setSkidInfo(val),
                            self.mdt.phys.vehicle.get_wheels()))
        self.__suspension_stiffness = CarParameter(
            'suspension_stiffness', self.mdt.phys.suspension_stiffness,
            (.5, -1.32), (0, 100),
            lambda val: map(lambda whl: whl.setSuspensionStiffness(val),
                            self.mdt.phys.vehicle.get_wheels()))
        self.__wheels_damping_relaxation = CarParameter(
            'wheels_damping_relaxation',
            self.mdt.phys.wheels_damping_relaxation, (.5, -1.4), (-1, 10),
            lambda val: map(lambda whl: whl.setWheelsDampingRelaxation(val),
                            self.mdt.phys.vehicle.get_wheels()))
        self.__wheels_damping_compression = CarParameter(
            'wheels_damping_compression',
            self.mdt.phys.wheels_damping_compression, (.5, -1.48), (-1, 10),
            lambda val: map(lambda whl: whl.setWheelsDampingCompression(val),
                            self.mdt.phys.vehicle.get_wheels()))
        self.__friction_slip = CarParameter(
            'friction_slip', self.mdt.phys.friction_slip, (.5, -1.56), (-1, 10),
            lambda val: map(lambda whl: whl.setFrictionSlip(val),
                            self.mdt.phys.vehicle.get_wheels()))
        self.__roll_influence = CarParameter(
            'roll_influence', self.mdt.phys.roll_influence,
            (.5, -1.64), (-1, 10),
            lambda val: map(lambda whl: whl.setRollInfluence(val),
                            self.mdt.phys.vehicle.get_wheels()))

        self.__pars = [
            self.__max_speed_par, self.__mass_par, self.__steering_min_speed,
            self.__steering_max_speed, self.__steering_clamp,
            self.__steering_inc, self.__steering_dec, self.__engine_acc_frc,
            self.__engine_dec_frc, self.__brake_frc, self.__pitch_control,
            self.__suspension_compression, self.__suspension_damping,
            self.__max_suspension_force, self.__max_suspension_travel_cm,
            self.__skid_info, self.__suspension_stiffness,
            self.__wheels_damping_relaxation, self.__wheels_damping_compression,
            self.__friction_slip, self.__roll_influence]
        self.speed_txt = OnscreenText(pos=(-.5, -.1), scale=.08,
            align=TextNode.ALeft, parent=eng.a2dTopRight, fg=(1, 1, 1, 1))

    def toggle(self):
        map(lambda par: par.toggle(), self.__pars)

    def destroy(self):
        Gui.destroy(self)
        map(lambda wdg: wdg.destroy(), self.__pars + [self.speed_txt])


class Car(GameObjectMdt):
    '''The Car class models a car.'''
    __metaclass__ = ABCMeta
    gfx_cls = _Gfx
    phys_cls = _Phys
    event_cls = _Event
    logic_cls = _Logic
    audio_cls = _Audio
    gui_cls = _Gui

    def __init__(self, pos, hpr):
        GameObjectMdt.__init__(self)
        self.gfx.nodepath.set_pos(pos)
        self.gfx.nodepath.set_hpr(hpr)
