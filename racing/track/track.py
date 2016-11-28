from racing.game.gameobject import GameObjectMdt
from .gfx import TrackGfx
from .phys import TrackPhys
from .gui.gui import TrackGui
from .event import TrackEvent


class Track(GameObjectMdt):

    def __init__(self, path, cb, split_world, submodels):
        eng.log_mgr.log('init track')
        self.path = path
        init_lst = [
            [('phys', TrackPhys, [self]),
             ('gfx', TrackGfx, [self, split_world, submodels],
              lambda: self.gfx.attach(self.on_loading)),
             ('gui', TrackGui, [self, path[6:]])],
            [('event', TrackEvent, [self])]]
        GameObjectMdt.__init__(self, init_lst, cb)

    def on_loading(self, txt):
        self.notify('on_loading', txt)
