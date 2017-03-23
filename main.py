# log ########################################################################
from os import path
from panda3d.core import MultiplexStream, Notify
from yorg.yorg import Yorg
import sys


if sys.platform != 'darwin' and not path.exists('main.py'):
    # (on osx it shows an error window on exit)
    # is it the deployed version?
    sys.stdout = open('yorg_output.txt', 'w')
    sys.stderr = open('yorg_error.txt', 'w')
    nout = MultiplexStream()
    Notify.ptr().setOstreamPtr(nout, 0)
    nout.addFile('yorg_log.txt')


# main #######################################################################
if __name__ == '__main__' or path.exists('main.pyo'):
    Yorg()
