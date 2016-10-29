from sys import exit
from ..gameobject import Event


class EngineEvent(Event):

    def __init__(self, mdt):
        Event.__init__(self, mdt)
        self.on_close_cb = lambda: None
        eng.base.win.setCloseRequestEvent('window-closed')
        self.accept('window-closed', self.__on_close)
        taskMgr.add(self.__on_frame, 'on frame')

    def register_close_cb(self, on_close_cb):
        self.on_close_cb = on_close_cb

    def __on_close(self):
        eng.base.closeWindow(eng.base.win)
        self.on_close_cb()
        exit()

    def __on_frame(self, task):
        self.notify('on_frame')
        return task.cont
