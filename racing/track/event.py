'''This module provides events for tracks.'''
from racing.game.gameobject.gameobject import Event


class _Event(Event):
    '''This class models track's events.'''

    def __init__(self, mdt):
        Event.__init__(self, mdt)
        self.accept('p', eng.pause.logic.toggle)
        self.tsk = None

    def start(self):
        '''Called at the start of the track.'''
        self.tsk = taskMgr.add(self.__on_frame, 'Track::__on_frame')

    def __on_frame(self, task):
        '''Called at each frame.'''
        cam_pos = eng.base.camera.get_pos()
        self.mdt.gfx.spot_lgt.setPos(cam_pos.x+60, cam_pos.y-60,
                                     cam_pos.z + 100)
        self.mdt.gfx.spot_lgt.lookAt(cam_pos.x-40, cam_pos.y+60,
                                     cam_pos.z - 50)
        self.mdt.gui.update_minimap()
        return task.again

    def destroy(self):
        Event.destroy(self)
        taskMgr.remove(self.tsk)
