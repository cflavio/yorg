from sys import platform
from os import environ, system
from webbrowser import open_new_tab
from panda3d.core import WindowProperties
from ...gameobject.gameobject import Gui


class EngineGui(Gui):

    def __init__(self, mdt):
        Gui.__init__(self, mdt)
        eng.base.disableMouse()
        resol = eng.logic.conf.win_size.split()
        self.set_resolution(tuple(int(size) for size in resol))
        if eng.logic.conf.fullscreen:
            self.toggle_fullscreen()
        self.pause_frame = None

    @staticmethod
    def open_browser(url):
        if platform.startswith('linux'):
            environ['LD_LIBRARY_PATH'] = ''
            system('xdg-open '+url)
        else:
            open_new_tab(url)

    @property
    def resolutions(self):
        d_i = eng.base.pipe.getDisplayInformation()

        def res(idx):
            return d_i.getDisplayModeWidth(idx), d_i.getDisplayModeHeight(idx)

        res_values = [res(idx) for idx in range(d_i.getTotalDisplayModes())]
        return sorted(list(set(res_values)))

    @property
    def resolution(self):
        win_prop = eng.base.win.get_properties()
        return win_prop.get_x_size(), win_prop.get_y_size()

    @property
    def closest_res(self):
        def distance(res):
            curr_res = self.resolution
            return abs(res[0] - curr_res[0]) + abs(res[1] - curr_res[1])

        dist_lst = map(distance, self.resolutions)
        try:
            idx_min = dist_lst.index(min(dist_lst))
            return self.resolutions[idx_min]
        except ValueError:  # sometimes we have empty resolutions
            return self.resolution

    def set_resolution(self, res, check=True):
        eng.log_mgr.log('setting resolution ' + str(res))
        props = WindowProperties()
        props.set_size(res)
        eng.base.win.request_properties(props)
        if not check:
            return
        args = 3.0, self.set_resolution_check, 'resolution check', [res]
        taskMgr.doMethodLater(*args)

    def set_resolution_check(self, res):
        res_msg = 'resolutions: {curr} (current), {res} (wanted)'
        eng.log_mgr.log(res_msg.format(curr=self.resolution, res=res))
        if self.resolution == res:
            return
        retry = 'second attempt: {curr} (current) {res} (wanted)'
        eng.log_mgr.log(retry.format(curr=self.resolution, res=res))
        self.set_resolution(res, False)

    def toggle_fullscreen(self):
        self.set_resolution(self.closest_res)
        props = WindowProperties()
        props.set_fullscreen(not eng.base.win.is_fullscreen())
        base.win.requestProperties(props)
