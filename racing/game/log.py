'''This module provides functionalities for logging.'''
from datetime import datetime
from platform import system, release
from panda3d.core import loadPrcFileData
from direct.directnotify.DirectNotify import DirectNotify


class LogMgr(object):
    '''This class models the log manager.'''

    def __init__(self):
        self.__notify = DirectNotify().newCategory('ya2')

    @staticmethod
    def configure():
        '''Presets the log manager.'''
        loadPrcFileData('', 'notify-level-ya2 info')

    def log(self, msg):
        '''Logs the message.'''
        str_time = datetime.now().strftime("%H:%M:%S")
        log_msg = '{time} {msg}'.format(time=str_time, msg=msg)
        self.__notify.info(log_msg)

    def log_conf(self):
        '''Logs the system configuration.'''
        self.log('version: ' + eng.version)
        self.log('operative system: ' + system() + ' ' + release())
        gsg = eng.win.get_gsg()
        self.log(gsg.getDriverVendor())
        self.log(gsg.getDriverRenderer())
        shad_maj = gsg.getDriverShaderVersionMajor()
        shad_min = gsg.getDriverShaderVersionMinor()
        self.log('shader: {maj}.{min}'.format(maj=shad_maj, min=shad_min))
        self.log(gsg.getDriverVersion())
        drv_maj = gsg.getDriverVersionMajor()
        drv_min = gsg.getDriverVersionMinor()
        drv = 'driver version: {maj}.{min}'
        self.log(drv.format(maj=drv_maj, min=drv_min))
        if not eng.win:
            return
        prop = eng.win.get_properties()
        self.log('fullscreen: ' + str(prop.get_fullscreen()))
        res_x, res_y = prop.get_x_size(), prop.get_y_size()
        res_tmpl = 'resolution: {res_x}x{res_y}'
        self.log(res_tmpl.format(res_x=res_x, res_y=res_y))
