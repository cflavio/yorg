from datetime import datetime
import platform
from panda3d.core import loadPrcFileData
from direct.directnotify.DirectNotify import DirectNotify


class LogMgr:

    def __init__(self):
        self.__notify = DirectNotify().newCategory('ya2')

    @staticmethod
    def configure():
        loadPrcFileData('', 'notify-level-ya2 info')

    def log(self, msg):
        self.__notify.info(datetime.now().strftime("%H:%M:%S") + ' ' + str(msg))

    def log_conf(self):
        self.log('version: '+eng.version)
        self.log('operative system: '+platform.system()+' '+platform.release())
        gsg = eng.win.get_gsg()
        self.log(gsg.getDriverVendor())
        self.log(gsg.getDriverRenderer())
        self.log('shader: %s.%s' % (gsg.getDriverShaderVersionMajor(), gsg.getDriverShaderVersionMinor()))
        self.log(gsg.getDriverVersion())
        self.log('driver version: %s.%s' % (gsg.getDriverVersionMajor(), gsg.getDriverVersionMinor()))
        if eng.win:
            prop = eng.win.get_properties()
            self.log('fullscreen: '+str(prop.get_fullscreen()))
            resolution = (prop.get_x_size(), prop.get_y_size())
            self.log('resolution: %sx%s' % resolution)
