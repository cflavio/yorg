'''This module provides functionalities for the GUI.'''
from panda3d.core import WindowProperties
from direct.showbase.DirectObject import DirectObject


class GuiMgr(DirectObject):
    '''This class models the GUI manager.'''

    def __init__(self, res):
        DirectObject.__init__(self)
        eng.disableMouse()
        self.set_resolution(res)
        if game.options['fullscreen']:
            self.toggle_fullscreen()
        eng.win.setCloseRequestEvent('window-closed')
        self.accept('window-closed', self.__on_close)

    @staticmethod
    def __on_close():
        '''Called when the application closes.'''
        if game.options['open_browser_at_exit']:
            eng.open_browser('http://www.ya2.it')
        eng.closeWindow(eng.win)
        exit()

    @property
    def resolutions(self):
        '''Available resolutions.'''
        d_i = eng.pipe.getDisplayInformation()

        def res(idx):
            '''Get the idx-th resolution.'''
            return d_i.getDisplayModeWidth(idx), d_i.getDisplayModeHeight(idx)

        res_values = [res(idx) for idx in range(d_i.getTotalDisplayModes())]
        sorted_res = sorted(list(set(res_values)))

        def res_str(res_x, res_y):
            '''Resolution as a string.'''
            return '{res_x}x{res_y}'.format(res_x=res_x, res_y=res_y)

        return [res_str(*s) for s in sorted_res]

    @property
    def resolution(self):
        '''Current resolution.'''
        win_prop = eng.win.get_properties()
        res_x, res_y = win_prop.get_x_size(), win_prop.get_y_size()
        return '{res_x}x{res_y}'.format(res_x=res_x, res_y=res_y)

    @property
    def closest_res(self):
        '''The closest resolution to the current one.'''
        def split_res(res):
            '''Gets the resolution values.'''
            return [int(v) for v in res.split('x')]

        def distance(res):
            '''Distance from a resolution.'''
            curr_res, res = split_res(self.resolution), split_res(res)
            return abs(res[0] - curr_res[0]) + abs(res[1] - curr_res[1])

        dist_lst = map(distance, self.resolutions)
        try:
            idx_min = dist_lst.index(min(dist_lst))
            return self.resolutions[idx_min]
        except ValueError:  # sometimes we have empty resolutions
            return self.resolution

    def set_resolution(self, res, check=True):
        '''Sets a resolution.'''
        eng.log_mgr.log('setting resolution ' + str(res))
        props = WindowProperties()
        props.set_size(*[int(resol) for resol in res.split('x')])
        eng.win.request_properties(props)
        if not check:
            return
        args = 3.0, self.set_resolution_check, 'resolution check', [res]
        taskMgr.doMethodLater(*args)

    def set_resolution_check(self, res):
        '''Checks the resolution.'''
        res_msg = 'resolutions: {curr} (current), {res} (wanted)'
        eng.log_mgr.log(res_msg.format(curr=self.resolution, res=res))
        if self.resolution == res:
            return
        retry = 'second attempt: {curr} (current) {res} (wanted)'
        self.log_mgr.log(retry.format(curr=self.resolution, res=res))
        self.set_resolution(res, False)

    def toggle_fullscreen(self):
        '''Toggles the fullscreen.'''
        self.set_resolution(self.closest_res)
        props = WindowProperties()
        props.set_fullscreen(not self.win.is_fullscreen())
        base.win.requestProperties(props)
