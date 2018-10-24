# log ########################################################################
import sys
from os.path import exists
from panda3d.core import MultiplexStream, Notify, Filename
from yorg.yorg import Yorg
from yyagl.lib.p3d.p3d import LibP3d
import direct.particles.ParticleManagerGlobal  # for deploy-ng


if sys.platform != 'darwin' and not exists('main.py'):
    # (on osx it shows an error window on exit)
    log_path = ''
    # is it the deployed windows version?
    if sys.platform == 'win32' and not exists('main.py'):
        log_path = LibP3d.fixpath(str(Filename.get_user_appdata_directory()) + '/Yorg')
        if not exists(log_path):
            Filename.mkdir(Filename(log_path))
    ofile = 'yorg_output.txt'
    opath = (log_path + '/' + ofile) if log_path else ofile
    sys.stdout = open(LibP3d.fixpath(opath), 'w')
    epath = (log_path + '/yorg_error.txt') if log_path else 'yorg_error.txt'
    sys.stderr = open(LibP3d.fixpath(epath), 'w')
    nout = MultiplexStream()
    Notify.ptr().setOstreamPtr(nout, 0)
    lpath = (log_path + '/yorg_log.txt') if log_path else 'yorg_log.txt'
    nout.addFile(lpath)


# main #######################################################################
if __name__ == '__main__' or exists('main.pyo'):
    yorg = Yorg()
    try:
        yorg.run()
    except Exception as e:
        import traceback; traceback.print_exc()
        # for windows:
        log_path = ''
        # is it the deployed windows version?
        if sys.platform == 'win32' and not exists('main.py'):
            log_path = LibP3d.fixpath(str(Filename.get_user_appdata_directory()) + '/Yorg')
            if not exists(log_path):
                Filename.mkdir(Filename(log_path))
        epath = (log_path + '/yorg_error.txt') if log_path else 'yorg_error.txt'
        with open(LibP3d.fixpath(epath), 'a') as f:
            import traceback; traceback.print_exc(file=f)
        yorg.kill()
