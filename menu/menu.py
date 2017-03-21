from yyagl.gameobject import GameObjectMdt, Gui
from yyagl.engine.gui.menu import MenuArgs, Menu
from .mainpage import YorgMainPage


class YorgMenuGui(Gui):

    def __init__(self, mdt, menu_args, opt_file, cars, car_path, phys_path,
                 tracks, tracks_tr, track_img):
        Gui.__init__(self, mdt)
        self.menu = Menu(menu_args)
        self.menu.logic.push_page(YorgMainPage(
            self.menu, opt_file, cars, car_path, phys_path, tracks, tracks_tr,
            track_img))

    def destroy(self):
        self.menu = self.menu.destroy()
        Gui.destroy(self)


class YorgMenu(GameObjectMdt):

    def __init__(self, menu_args, opt_file, cars, car_path, phys_path, tracks,
                 tracks_tr, track_img):
        init_lst = [[('gui', YorgMenuGui, [
            self, menu_args, opt_file, cars, car_path, phys_path, tracks,
            tracks_tr, track_img])]]
        GameObjectMdt.__init__(self, init_lst)
