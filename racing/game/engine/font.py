from ..gameobject.gameobject import Colleague


class FontMgr(Colleague):

    def __init__(self, mdt):
        Colleague.__init__(self, mdt)
        self.__fonts = {}

    def load_font(self, path):
        if path not in self.__fonts:
            self.__fonts[path] = eng.base.loader.loadFont(path)
            self.__fonts[path].setPixelsPerUnit(60)
            self.__fonts[path].setOutline((0, 0, 0, 1), .8, .2)
        return self.__fonts[path]
