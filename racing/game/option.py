import yaml


class OptionMgr:

    @staticmethod
    def get_options():
        try:
            with open('options.yml') as opt_file:
                conf = yaml.load(opt_file)
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
        with open('options.yml', 'w') as opt_file:
            yaml.dump(conf, opt_file, default_flow_style=False)
