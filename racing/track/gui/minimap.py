from direct.gui.OnscreenImage import OnscreenImage


class Minimap(object):

    def __init__(self, track, lrtb):
        self.lrtb = lrtb
        #TODO: pass arguments font, color, sfx, ...
        self.minimap = OnscreenImage(
            'assets/images/minimaps/%s.jpg' % track, pos=(-.25, 1, .25),
            scale=.2, parent=eng.base.a2dBottomRight)
        self.car_handle = OnscreenImage(
            'assets/images/minimaps/car_handle.png', pos=(-.25, 1, .25),
            scale=.03, parent=eng.base.a2dBottomRight)
        self.car_handle.setTransparency(True)

    def update(self):
        #TODO: race object which has references to the track and the car, it
        # attaches to the car and updates the minimap
        left, right, top, bottom = self.lrtb
        car_pos = game.player_car.gfx.nodepath.get_pos()
        pos_x_norm = (car_pos.getX() - left) / (right - left)
        pos_y_norm = (car_pos.getY() - bottom) / (top - bottom)

        width = self.minimap.getScale()[0] * 2.0
        height = self.minimap.getScale()[2] * 2.0
        center_x, center_y = self.minimap.getX(), self.minimap.getZ()
        left_img = center_x - width / 2.0
        bottom_img = center_y - height / 2.0
        pos_x = left_img + pos_x_norm * width
        pos_y = bottom_img + pos_y_norm * height
        self.car_handle.set_pos(pos_x, 1, pos_y)
        self.car_handle.setR(-game.player_car.gfx.nodepath.getH())

    def destroy(self):
        map(lambda wdg: wdg.destroy(), [self.minimap, self.car_handle])
