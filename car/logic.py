from ya2.gameobject import Logic


class _Logic(Logic):
    '''This class manages the events of the Car class.'''

    def __init__(self, mdt):
        Logic.__init__(self, mdt)
        self.__steering = 0  # degrees
        self.last_time_start = 0

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
        self.mdt.gui.speed_txt.setText(str(round(self.mdt.phys.speed, 2)))
        if not self.mdt.event.has_just_started:
            self.mdt.gui.time_txt.setText(str(round(
                globalClock.getFrameTime() - self.last_time_start, 2)))
