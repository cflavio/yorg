'''This module defines the option manager.'''
from yaml import load, dump


class DictFile(object):
    '''This class defines the option manager.'''

    def __init__(self, path, default_dct={}):
        self.path = path
        try:
            with open(path) as yaml_file:
                self.dct = load(yaml_file)
        except IOError:
            self.dct = default_dct

    def store(self):
        '''Stores the current dict.'''
        with open(self.path, 'w') as yaml_file:
            dump(self.dct, yaml_file, default_flow_style=False)

    def __getitem__(self, arg):
        return self.dct[arg]

    def __setitem__(self, arg, val):
        self.dct[arg] = val

    def __delitem__(self, arg):
        del self.dct[arg]
