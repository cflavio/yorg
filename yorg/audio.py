from yyagl.gameobject import Audio


class YorgAudio(Audio):

    def __init__(self, mdt):
        Audio.__init__(self, mdt)
        bg_menu = 'assets/music/Inizio - Start Your Engines.ogg'
        self.menu_music = loader.loadSfx(bg_menu)
        self.menu_music.set_loop(True)
