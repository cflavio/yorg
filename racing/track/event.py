from racing.game.gameobject import Event


class TrackEvent(Event):

    def __init__(self, mdt):
        Event.__init__(self, mdt)

    def start(self):
        eng.event.attach(self.on_frame)

    def on_frame(self):
        cam_pos = game.player_car.logic.camera.camera.get_pos()
        if not game.options['development']['shaders']:
            self.mdt.gfx.spot_lgt.setPos(cam_pos + (60, -60, 100))
            self.mdt.gfx.spot_lgt.lookAt(cam_pos + (-40, 60, -50))
        self.mdt.gui.minimap.update(game.player_car.gfx.nodepath.get_pos())

    def destroy(self):
        Event.destroy(self)
        eng.event.detach(self.on_frame)
