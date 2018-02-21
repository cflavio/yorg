# log ########################################################################
import sys
from os.path import exists, join
from panda3d.core import MultiplexStream, Notify, Filename
from yorg.yorg import Yorg
import direct.particles.ParticleManagerGlobal  # for deploy-ng


if sys.platform != 'darwin' and not exists('main.py'):
    # (on osx it shows an error window on exit)
    log_path = ''
    # is it the deployed windows version?
    if sys.platform == 'win32' and not exists('main.py'):
        log_path = join(str(Filename.get_user_appdata_directory()), 'Yorg')
        if not exists(log_path):
            Filename.mkdir(Filename(log_path))
    ofile = 'yorg_output.txt'
    opath = join(log_path, ofile) if log_path else ofile
    sys.stdout = open(opath, 'w')
    epath = join(log_path, 'yorg_error.txt') if log_path else 'yorg_error.txt'
    sys.stderr = open(epath, 'w')
    nout = MultiplexStream()
    Notify.ptr().setOstreamPtr(nout, 0)
    lpath = join(log_path, 'yorg_log.txt') if log_path else 'yorg_log.txt'
    nout.addFile(lpath)


# main #######################################################################
if __name__ == '__main__' or exists('main.pyo'):
    yorg = Yorg()
    #try:
    yorg.run()
    #except Exception as e:
    #    print e
    #    import traceback; traceback.print_stack()
    #    yorg.kill()
