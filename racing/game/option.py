'''This module defines the option manager.'''
from yaml import load, dump


class OptionMgr(object):
    '''This class defines the option manager.'''

    def __init__(self):
        pass

    @staticmethod
    def get_options():
        '''It returns the current option dict.'''
        try:
            with open('options.yml') as opt_file:
                conf = load(opt_file)
        except IOError:
            conf = {
                'lang': 0,
                'volume': 1,
                'fullscreen': 0,
                'resolution': '1280 720',
                'aa': 0,
                'multithreaded_render': 0,
                'open_browser_at_exit': 1,
                'ai': 0,
                'submodels': 1,
                'split_world': 1,
                'laps': 3,
                'fps': 1}
        return conf

    @staticmethod
    def set_options(conf):
        '''It stores the conf dict.'''
        with open('options.yml', 'w') as opt_file:
            dump(conf, opt_file, default_flow_style=False)
