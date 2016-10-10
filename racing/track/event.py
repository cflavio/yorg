from racing.game.gameobject.gameobject import Event


class _Event(Event):

    def __init__(self, mdt):
        Event.__init__(self, mdt)
        self.accept('p', eng.gui.toggle_pause)

    def start(self):
        self.tsk = taskMgr.add(self.__on_frame, 'Track::__on_frame')

    def __on_frame(self, task):
        cam_pos = eng.base.camera.get_pos()
        self.mdt.gfx.spot_lgt.setPos(cam_pos.x+60, cam_pos.y-60, cam_pos.z + 100)
        self.mdt.gfx.spot_lgt.lookAt(cam_pos.x-40, cam_pos.y+60, cam_pos.z - 50)
        self.mdt.gui.update_minimap()
        return task.again

    def destroy(self):
        Event.destroy(self)
        taskMgr.remove(self.tsk)
