from ya2.gameobject import Event


class _Event(Event):

    def __init__(self, mdt):
        Event.__init__(self, mdt)
        self.accept('on_frame', self.__on_frame)
        self.accept('p', eng.toggle_pause)

    def __on_frame(self):
        cam_pos = eng.camera.get_pos()
        self.mdt.gfx.spot_lgt.setPos(cam_pos.x+60, cam_pos.y-60, cam_pos.z + 100)
        self.mdt.gfx.spot_lgt.lookAt(cam_pos.x-40, cam_pos.y+60, cam_pos.z - 50)
        self.mdt.gui.update_minimap()
