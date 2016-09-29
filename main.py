# log ########################################################################
from os import path
from panda3d.core import MultiplexStream, Notify
import sys
from racing.game.configuration import Configuration
from racing.game.option import OptionMgr
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
    conf = Configuration(
            fps=OptionMgr.get_options()['fps'],
            win_title='Yorg',
            win_size=OptionMgr.get_options()['resolution'],
            fullscreen=OptionMgr.get_options()['fullscreen'],
            antialiasing=OptionMgr.get_options()['aa'],
            mt_render=OptionMgr.get_options()['multithreaded_render'])
    Yorg(conf,
        'yorg').run()
