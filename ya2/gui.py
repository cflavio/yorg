from direct.gui.DirectButton import DirectButton
from direct.gui.OnscreenText import OnscreenText
from itertools import product
from panda3d.core import PNMImage, Texture
from panda3d.core import TextNode
from direct.gui.OnscreenImage import OnscreenImage


class ImageButton(DirectButton):

    def __init__(self, eng, image, *args, **kwargs):
        maps = eng.loader.loadModel('ya2/assets/img_btn')
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


def transl_text(obj, text_src, text_transl):
    # we get text_transl to put it into po files
    obj.__text_src = text_src
    obj.__class__.transl_text = property(lambda self: _(self.__text_src))


def may_destroy(wdg):
    try:
        wdg.destroy()
    except AttributeError:  # wdg may be None
        pass


class PageArgs(object):

    def __init__(self, fsm, font, btn_size, btn_color, back, social, version):
        self.fsm = fsm
        self.font = font
        self.btn_size = btn_size
        self.btn_color = btn_color
        self.back = back
        self.social = social
        self.version = version


class Page(object):

    def __init__(self, page_args):
        self.page_args = page_args
        self.font = eng.font_mgr.load_font(page_args.font)

    def create(self):
        self.update_texts()
        if self.page_args.back:
            self.__set_back_btn()
        if self.page_args.social:
            self.__set_social()
        if self.page_args.version:
            self.__set_version()
        self.background = OnscreenImage(
            scale=(1.77778, 1, 1.0),
            image='assets/images/gui/menu_background.jpg')
        self.background.setBin( 'background', 10 )
        self.widgets += [self.background]

    def update_texts(self):
        transl_wdg = [wdg for wdg in self.widgets
                      if hasattr(wdg, 'transl_text')]
        for wdg in transl_wdg:
            wdg['text'] = wdg.transl_text

    def __set_back_btn(self):
        page_args = self.page_args
        self.widgets += [DirectButton(
            text='', scale=.12, pos=(0, 1, -.8), text_font=self.font,
            text_fg=(.75, .75, .75, 1),
            frameColor=page_args.btn_color, frameSize=page_args.btn_size,
            command=self.__on_back,
            rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
            clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))]
        transl_text(self.widgets[-1], 'Back', _('Back'))
        self.widgets[-1]['text'] = self.widgets[-1].transl_text

    def __on_back(self):
        self.on_back()
        self.page_args.fsm.demand('Main')

    def on_back(self):
        pass

    def __set_social(self):
        sites = [('facebook', 'http://www.facebook.com/Ya2Tech'),
                 ('twitter', 'http://twitter.com/ya2tech'),
                 ('google_plus',
                  'https://plus.google.com/118211180567488443153'),
                 ('youtube',
                  'http://www.youtube.com/user/ya2games?sub_confirmation=1'),
                 ('pinterest', 'http://www.pinterest.com/ya2tech'),
                 ('tumblr', 'http://ya2tech.tumblr.com'),
                 ('feed', 'http://www.ya2.it/feed-following')]
        self.widgets += [
            ImageButton(eng, parent=eng.a2dBottomRight, scale=.1,
                        pos=(-1.0 + i*.15, 1, .1), frameColor=(0, 0, 0, 0),
                        image='assets/images/icons/%s_png.png' % site[0],
                        command=eng.open_browser, extraArgs=[site[1]],
                        rolloverSound=loader.loadSfx('assets/sfx/menu_over.wav'),
                        clickSound=loader.loadSfx('assets/sfx/menu_clicked.ogg'))
            for i, site in enumerate(sites)]

    def __set_version(self):
        self.widgets += [
            OnscreenText(text=eng.version, parent=eng.a2dBottomLeft,
                         pos=(.02, .02), scale=.04, fg=(.8, .8, .8, 1),
                         align=TextNode.ALeft, font=self.font)]

    def destroy(self):
        map(lambda wdg: wdg.destroy(), self.widgets)