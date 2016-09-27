from direct.gui.DirectButton import DirectButton
from panda3d.core import PNMImage, Texture
from itertools import product


class ImageButton(DirectButton):

    def __init__(self, eng, image, *args, **kwargs):
        maps = eng.loader.loadModel('racing/game/assets/img_btn')
        btn_geom = (maps.find('**/image'), maps.find('**/image'),
                    maps.find('**/image_rollover'))
        DirectButton.__init__(self, geom=btn_geom, *args, **kwargs)
        image_rollover = PNMImage(image)
        for x, y in product(range(image_rollover.get_x_size()),
                            range(image_rollover.get_y_size())):
            col = image_rollover.getXelA(x, y)
            new_color = (col[0] * 1.2, col[1] * 1.2, col[2] * 1.2, col[3])
            image_rollover.setXelA(x, y, new_color)
        rollover_texture = Texture()
        rollover_texture.load(image_rollover)
        for i, texture in enumerate([eng.loader.loadTexture(image),
                                     eng.loader.loadTexture(image),
                                     rollover_texture]):
            self['geom'][i].setTexture(texture, 1)
            self['geom'][i].setTransparency(True)
        self.initialiseoptions(self.__class__)
