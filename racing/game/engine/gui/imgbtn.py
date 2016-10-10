'''This module provides an image button.'''
from direct.gui.DirectButton import DirectButton
from panda3d.core import PNMImage, Texture
from itertools import product
from os.path import dirname, realpath


class ImageButton(DirectButton):
    '''This class models an image button.'''

    def __init__(self, image, *args, **kwargs):
        this_path = dirname(realpath(__file__))
        maps = loader.loadModel(this_path + '/../../assets/img_btn')
        imgs = ['image', 'image', 'image_rollover']
        btn_geom = [maps.find('**/' + img) for img in imgs]
        DirectButton.__init__(self, geom=btn_geom, *args, **kwargs)
        img_rollover = PNMImage(image)
        sz_x, sz_y = img_rollover.get_x_size(), img_rollover.get_y_size()
        for pos_x, pos_y in product(range(sz_x), range(sz_y)):
            col = img_rollover.getXelA(pos_x, pos_y)
            new_color = (col[0] * 1.2, col[1] * 1.2, col[2] * 1.2, col[3])
            img_rollover.setXelA(pos_x, pos_y, new_color)
        rollover_txt = Texture()
        rollover_txt.load(img_rollover)
        txt = loader.loadTexture(image)
        for i, texture in enumerate([txt, txt, rollover_txt]):
            self['geom'][i].setTexture(texture, 1)
            self['geom'][i].setTransparency(True)
        self.initialiseoptions(self.__class__)
