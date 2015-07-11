from ya2.gameobject import Audio


class _Audio(Audio):

    def __init__(self, mdt):
        Audio.__init__(self, mdt)
        self.countdown_sfx = loader.loadSfx('assets/sfx/countdown.ogg')
