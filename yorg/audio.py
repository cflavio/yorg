'''This module provides Yorg's audio.'''
from racing.game.gameobject.gameobject import Audio


class _Audio(Audio):
    '''This class defines Yorg's audio.'''

    def __init__(self, mdt):
        Audio.__init__(self, mdt)
        self.menu_music = loader.loadSfx('assets/music/menu.ogg')
        self.game_music = loader.loadSfx('assets/music/on_the_other_side.ogg')
        map(lambda mus: mus.set_loop(True), [self.menu_music, self.game_music])
