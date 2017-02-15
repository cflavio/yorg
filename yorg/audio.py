from yyagl.gameobject import Audio


class _Audio(Audio):

    def __init__(self, mdt):
        Audio.__init__(self, mdt)
        self.menu_music = loader.loadSfx('assets/music/Start Your Engines.ogg')
        self.menu_music.set_loop(True)
