from racing.game.gameobject.gameobject import Event


class _Event(Event):

    def __init__(self, mdt):
        self.tsk = None
        Event.__init__(self, mdt)
        self.accept('p', eng.pause.logic.toggle)

    def start(self):
        eng.event.attach(self)

    def on_frame(self):
        cam_pos = eng.base.camera.get_pos()
        self.mdt.gfx.spot_lgt.setPos(cam_pos + (60, -60, 100))
        self.mdt.gfx.spot_lgt.lookAt(cam_pos + (-40, 60, -50))
        self.mdt.gui.minimap.update()

    def destroy(self):
        Event.destroy(self)
        eng.event.detach(self)
