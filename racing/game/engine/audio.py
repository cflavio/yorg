from panda3d.core import AudioSound
from ..gameobject import Audio


class EngineAudio(Audio):

    @staticmethod
    def play(sound):
        if sound.status() != AudioSound.PLAYING:
            sound.play()
