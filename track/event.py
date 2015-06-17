from ya2.gameobject import Event


class _Event(Event):

    def evt_OnFrame(self, evt):
        cam_pos = eng.camera.get_pos()
        self.mdt.gfx.spot_lgt.setPos(cam_pos.x+60, cam_pos.y-60, cam_pos.z + 100)
        self.mdt.gfx.spot_lgt.lookAt(cam_pos.x-40, cam_pos.y+60, cam_pos.z - 50)
