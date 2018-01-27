from yyagl.gameobject import AudioColleague


class YorgAudio(AudioColleague):

    def __init__(self, mediator):
        AudioColleague.__init__(self, mediator)
        bg_menu = 'assets/music/Inizio - Start Your Engines.ogg'
        self.menu_music = loader.loadSfx(bg_menu)
        self.menu_music.set_loop(True)
