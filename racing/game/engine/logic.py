'''This module defines engine's logic.'''
from ..gameobject.gameobject import Logic
from .configuration import Configuration


class EngineLogic(Logic):
    '''This class models the engine object.'''

    def __init__(self, mdt, configuration=None):
        Logic.__init__(self, mdt)
        self.conf = configuration or Configuration()

    @property
    def version(self):
        '''The current software version.'''
        if eng.base.appRunner:
            package = eng.base.appRunner.p3dInfo.FirstChildElement('package')
            return 'version: ' + package.Attribute('version')
        return 'version: source'
