from direct.gui.OnscreenImage import OnscreenImage


class Minimap(object):

    def __init__(self, track, lrtb):
        self.lrtb = lrtb
        self.minimap = OnscreenImage(
            'assets/images/minimaps/%s.jpg' % track, pos=(-.25, 1, .25),
            scale=.2, parent=eng.base.a2dBottomRight)
        self.car_handle = OnscreenImage(
            'assets/images/minimaps/car_handle.png', pos=(-.25, 1, .25),
            scale=.03, parent=eng.base.a2dBottomRight)
        self.car_handle.setTransparency(True)
        self.width = self.minimap.getScale()[0] * 2.0
        self.height = self.minimap.getScale()[2] * 2.0
        center_x, center_y = self.minimap.getX(), self.minimap.getZ()
        self.left_img = center_x - self.width / 2.0
        self.bottom_img = center_y - self.height / 2.0

    def update(self, car_pos):
        left, right, top, bottom = self.lrtb
        pos_x_norm = (car_pos.getX() - left) / (right - left)
        pos_y_norm = (car_pos.getY() - bottom) / (top - bottom)
        pos_x = self.left_img + pos_x_norm * self.width
        pos_y = self.bottom_img + pos_y_norm * self.height
        self.car_handle.set_pos(pos_x, 1, pos_y)
        self.car_handle.setR(-game.player_car.gfx.nodepath.getH())

    def destroy(self):
        map(lambda wdg: wdg.destroy(), [self.minimap, self.car_handle])
