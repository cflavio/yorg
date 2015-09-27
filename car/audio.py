from panda3d.core import AudioSound
from ya2.gameobject import Audio


class _Audio(Audio):

    def __init__(self, mdt):
        Audio.__init__(self, mdt)
        self.engine_sfx = loader.loadSfx('assets/sfx/engine.ogg')
        self.brake_sfx = loader.loadSfx('assets/sfx/brake.ogg')
        self.crash_sfx = loader.loadSfx('assets/sfx/crash.ogg')
        self.crash_high_speed_sfx = loader.loadSfx('assets/sfx/crash_high_speed.ogg')
        self.lap_sfx = loader.loadSfx('assets/sfx/lap.ogg')
        self.landing_sfx = loader.loadSfx('assets/sfx/landing.ogg')
        map(lambda sfx: sfx.set_loop(True), [self.engine_sfx, self.brake_sfx])
        self.engine_sfx.play()

    def update(self, input_dct):
        if input_dct['reverse'] and self.mdt.phys.speed > 50.0 and \
                self.brake_sfx.status() != AudioSound.PLAYING and \
                not self.mdt.phys.is_flying:
            self.brake_sfx.play()
        if not input_dct['reverse'] or self.mdt.phys.speed < 50.0 or self.mdt.phys.is_flying:
            self.brake_sfx.stop()
        speed_ratio = self.mdt.phys.speed / self.mdt.phys.max_speed
        self.engine_sfx.set_volume(max(.25, abs(speed_ratio)))

    def destroy(self):
        self.engine_sfx.stop()
