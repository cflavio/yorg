# log ########################################################################
from os import path
from panda3d.core import MultiplexStream, Notify
import sys
from racing.game.configuration import Configuration
from racing.game.dictfile import DictFile
from yorg import Yorg


if sys.platform != 'darwin' and \
        not path.exists('main.py'):  # on osx it shows an error window on exit
    #is it the deployed version?
    sys.stdout = open('yorg_output.txt', 'w')
    sys.stderr = open('yorg_error.txt', 'w')
    nout = MultiplexStream()
    Notify.ptr().setOstreamPtr(nout, 0)
    nout.addFile('yorg_log.txt')


# main #######################################################################
if __name__ == '__main__' or path.exists('main.pyo'):
    default_opt = {
        'lang': 'en',
        'volume': 1,
        'fullscreen': 0,
        'resolution': '1280 720',
        'aa': 0,
        'multithreaded_render': 0,
        'open_browser_at_exit': 1,
        'ai': 0,
        'submodels': 1,
        'split_world': 1,
        'laps': 3,
        'fps': 1}
    options = DictFile('options.yml', default_opt)
    conf = Configuration(
            fps=options['fps'],
            win_title='Yorg',
            win_size=options['resolution'],
            fullscreen=options['fullscreen'],
            antialiasing=options['aa'],
            mt_render=options['multithreaded_render'])
    Yorg(conf, 'yorg', ['English', 'Italiano'], options)
