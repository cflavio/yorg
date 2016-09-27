from panda3d.core import TextNode
from direct.gui.DirectSlider import DirectSlider
from direct.gui.OnscreenText import OnscreenText
from racing.game.gameobject import Gui
from direct.gui.OnscreenImage import OnscreenImage


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
        self.panel = OnscreenImage(
            'assets/images/gui/panel.png', scale=(.4, 1, .2),
            parent=eng.a2dTopRight, pos=(-.45, 1, -.25))
        self.panel.setTransparency(True)
        self.speed_txt = OnscreenText(
            pos=(-.7, -.38), scale=.065,
            font=eng.font_mgr.load_font('assets/fonts/zekton rg.ttf'),
            parent=eng.a2dTopRight, fg=(1, 1, 1, 1))
        self.lap_txt = OnscreenText(
            text='1/3', pos=(-.5, -.38), scale=.065,
            font=eng.font_mgr.load_font('assets/fonts/zekton rg.ttf'),
            parent=eng.a2dTopRight, fg=(1, 1, 1, 1))
        self.time_txt = OnscreenText(
            pos=(-.3, -.38), scale=.065,
            font=eng.font_mgr.load_font('assets/fonts/zekton rg.ttf'),
            parent=eng.a2dTopRight, fg=(1, 1, 1, 1))
        self.best_txt = OnscreenText(
            pos=(-.1, -.38), scale=.065,
            font=eng.font_mgr.load_font('assets/fonts/zekton rg.ttf'),
            parent=eng.a2dTopRight, fg=(1, 1, 1, 1))

    def toggle(self):
        map(lambda par: par.toggle(), self.__pars)

    def destroy(self):
        Gui.destroy(self)
        labels = [self.panel, self.speed_txt, self.time_txt, self.lap_txt,
                  self.best_txt]
        map(lambda wdg: wdg.destroy(), self.__pars + labels)
