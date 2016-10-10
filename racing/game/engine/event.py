'''This module manages engine's events.'''
from sys import exit
from ..gameobject.gameobject import Event


class EngineEvent(Event):
    '''This class models the GUI manager.'''

    def __init__(self, mdt):
        Event.__init__(self, mdt)
        self.on_close_cb = lambda: None
        eng.base.win.setCloseRequestEvent('window-closed')
        self.accept('window-closed', self.__on_close)
        taskMgr.add(self.__on_frame, 'on frame')

    def register_close_cb(self, on_close_cb):
        '''Registers the closing callback.'''
        self.on_close_cb = on_close_cb

    def __on_close(self):
        '''Called when the application closes.'''
        eng.base.closeWindow(eng.base.win)
        self.on_close_cb()
        exit()

    def __on_frame(self, task):
        '''Called at each frame.'''
        self.notify()
        return task.cont
