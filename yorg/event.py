import time
from racing.game.gameobject.gameobject import Event


class _Event(Event):
    '''This class manages the events of the game.'''

    def __init__(self, mdt):
        Event.__init__(self, mdt)
        self.accept('f12', eng.phys.toggle_debug)
        now = time.strftime('%y_%m_%d_%H_%M_%S')
        self.accept('f10', eng.base.win.saveScreenshot, ['yorg_' + now + '.png'])

    def on_end(self):
        if self.mdt.options['open_browser_at_exit']:
            eng.open_browser('http://www.ya2.it')
