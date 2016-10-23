from panda3d.core import loadPrcFileData
from .log import LogMgr


class Configuration(object):

    def __init__(
            self, fps=False, win_size='1280 720', win_title='Ya2',
            fullscreen=False, cursor_hidden=False, sync_video=True,
            antialiasing=False, profiling=False, mt_render=False,
            model_path='assets/models', lang='en', lang_path='assets/locale',
            lang_domain='ya2_game', languages=['English', 'Italiano']):
        self.fps = fps
        self.win_size = win_size
        self.win_title = win_title
        self.fullscreen = fullscreen
        self.cursor_hidden = cursor_hidden
        self.sync_video = sync_video
        self.antialiasing = antialiasing
        self.multithreaded_render = mt_render
        self.profiling = profiling
        self.model_path = model_path
        self.lang = lang
        self.lang_path = lang_path
        self.lang_domain = lang_domain
        self.languages = languages
        self.configure()

    @staticmethod
    def __set(key, value):
        loadPrcFileData('', key + ' ' + str(value))

    def configure(self):
        self.__set('show-frame-rate-meter', int(self.fps))
        if self.win_size:
            self.__set('win-size', self.win_size)
        self.__set('window-title', self.win_title)
        self.__set('cursor-hidden', int(self.cursor_hidden))
        self.__set('sync-video', int(self.sync_video))
        if self.antialiasing:
            self.__set('framebuffer-multisample', 1)
            self.__set('multisamples', 2)
        if self.multithreaded_render:
            self.__set('threading-model', '/Draw')
        if self.profiling:
            self.__set('want-pstats', 1)
            self.__set('task-timer-verbose', 1)
            self.__set('pstats-tasks', 1)
            self.__set('gl-finish', 1)
            self.__set('pstats-host', '127.0.0.1')
        LogMgr.configure()
