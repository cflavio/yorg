from racing.game.gameobject import Event


class _Event(Event):

    def __init__(self, mdt):
        self.tsk = None
        Event.__init__(self, mdt)
        self.accept('p', eng.pause.logic.toggle)

    def start(self):
        eng.event.attach(self.on_frame)

    def on_frame(self):
        cam_pos = eng.base.camera.get_pos()
        self.mdt.gfx.spot_lgt.setPos(cam_pos + (60, -60, 100))
        self.mdt.gfx.spot_lgt.lookAt(cam_pos + (-40, 60, -50))
        self.mdt.gui.minimap.update(game.player_car.gfx.nodepath.get_pos())

    def destroy(self):
        Event.destroy(self)
        eng.event.detach(self.on_frame)
