'''This module provides the audio for tracks.'''
from racing.game.gameobject.gameobject import Audio


class _Audio(Audio):
    '''This class models track's audio.'''

    def __init__(self, mdt):
        Audio.__init__(self, mdt)
        self.countdown_sfx = loader.loadSfx('assets/sfx/countdown.ogg')
