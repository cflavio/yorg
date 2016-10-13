'''This module provides physics functionalities.'''
from panda3d.bullet import BulletWorld, BulletDebugNode
from ..gameobject.gameobject import Phys


class EnginePhys(Phys):
    '''This class models the physics manager.'''

    def __init__(self, mdt):
        Phys.__init__(self, mdt)
        self.collision_objs = []  # objects to be tested
        self.__coll_dct = {}  # obj: [(node, coll_time), ...]
        self.world_phys = None
        self.__debug_np = None

    def init(self):
        '''Inits the physics.'''
        self.collision_objs = []
        self.__coll_dct = {}
        self.world_phys = BulletWorld()
        self.world_phys.setGravity((0, 0, -9.81))
        debug_node = BulletDebugNode('Debug')
        debug_node.showBoundingBoxes(True)
        self.__debug_np = render.attachNewNode(debug_node)
        self.world_phys.setDebugNode(self.__debug_np.node())

    def start(self):
        '''Starts the physics.'''
        eng.event.attach(self._on_frame, 2)

    def _on_frame(self):
        '''Called on each frame.'''
        self.world_phys.doPhysics(globalClock.getDt(), 10, 1/180.0)
        self.__do_collisions()

    def stop(self):
        '''Stops the physics.'''
        self.world_phys = None
        self.__debug_np.removeNode()
        eng.event.detach(self._on_frame)

    def __process_contact(self, obj, node, to_clear):
        '''Processes a physics contact.'''
        if node == obj:
            return
        if obj in to_clear:
            to_clear.remove(obj)
        if node in [coll_pair[0] for coll_pair in self.__coll_dct[obj]]:
            return
        self.__coll_dct[obj] += [(node, globalClock.getFrameTime())]
        self.notify(obj, node.getName())

    def __do_collisions(self):
        '''Computes the collisions.'''
        to_clear = self.collision_objs[:]
        for obj in self.collision_objs:
            if not obj in self.__coll_dct:
                self.__coll_dct[obj] = []
            result = self.world_phys.contactTest(obj)
            for contact in result.getContacts():
                self.__process_contact(obj, contact.getNode0(), to_clear)
                self.__process_contact(obj, contact.getNode1(), to_clear)
        for obj in to_clear:
            for coll_pair in self.__coll_dct[obj]:
                if globalClock.getFrameTime() - coll_pair[1] > .25:
                    self.__coll_dct[obj].remove(coll_pair)

    def toggle_debug(self):
        '''Toggles the physics debug.'''
        is_hidden = self.__debug_np.isHidden()
        (self.__debug_np.show if is_hidden else self.__debug_np.hide)()
