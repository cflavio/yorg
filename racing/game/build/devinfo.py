'''Builds info for developers.'''
from os import system
from .build import path, ver_branch, exec_cmd, \
    devinfo_path_str


def build_devinfo(target, source, env):
    '''This function creates the
    `pep8 <https://www.python.org/dev/peps/pep-0008>`_,
    `Pylint <http://www.pylint.org>`_ and
    `pyflakes <https://pypi.python.org/pypi/pyflakes>`_ code reports.'''
    name = env['NAME']

    def clean_pylint(pylint_out):
        '''Cleans pylint stuff.'''
        clean_out = ''
        skipping = False
        for line in pylint_out.split('\n'):
            if line != 'No config file found, using default configuration':
                if line == 'Traceback (most recent call last):':
                    skipping = True
                elif line == 'RuntimeError: maximum recursion depth ' +\
                             'exceeded while calling a Python object':
                    skipping = False
                elif not skipping:
                    clean_out += line + '\n'
        return clean_out

    def process(name, cond):
        '''Processes files which don't satisfy cond.'''
        for s in source:
            with open(name % path, 'a') as f:
                if cond(s):
                    continue
                f.write('    '+str(s)+'\n')
                outs = [clean_pylint((exec_cmd('pylint -r n '+str(s)))),
                        exec_cmd('pyflakes '+str(s)),
                        exec_cmd('pep8 '+str(s))]
                outs = [out.strip() for out in outs]
                for out in outs:
                    if out:
                        f.write(out+'\n')
                f.write('\n')

    process('%sdevinfo.txt', lambda s: str(s).startswith('racing'))

    def racing_cond(s):
        '''The condition for the racing package.'''
        _s = str(s)
        return not _s.startswith('racing') or _s.startswith('racing/game/')

    process('%sdevinfo_racing.txt', racing_cond)

    def game_cond(s):
        '''The condition for the game package.'''
        not_game = not str(s).startswith('racing/game/')
        thirdparty = str(s).startswith('racing/game/thirdparty')
        return not_game or thirdparty or str(s).startswith('racing/game/tests')

    process('%sdevinfo_game.txt', game_cond)
    build_command_str = \
        "tar -czf {out_name} -C {path} devinfo.txt devinfo_racing.txt " + \
        "devinfo_game.txt && rm {path}devinfo.txt " + \
        "{path}devinfo_racing.txt {path}devinfo_game.txt"
    fpath = devinfo_path_str.format(path=path, name=name, version=ver_branch)
    build_command = build_command_str.format(path=path, out_name=fpath)
    system(build_command)
