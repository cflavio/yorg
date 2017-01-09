import time
import sys
from yyagl.gameobject import Event


class _Event(Event):

    def __init__(self, mdt):
        Event.__init__(self, mdt)
        self.accept('f12', eng.phys.toggle_debug)
        fname = 'yorg_' + time.strftime('%y_%m_%d_%H_%M_%S') + '.png'
        self.accept('f10', eng.base.win.saveScreenshot, [fname])
        base.accept('escape-up', self.on_end)

    def on_end(self):
        if self.mdt.options['settings']['open_browser_at_exit']:
            eng.gui.open_browser('http://www.ya2.it')
        sys.exit()
