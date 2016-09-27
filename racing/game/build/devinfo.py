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

    #Waiting for Panda 1.9.0 to uncomment this
    #with open('%sdevinfo.txt' % path, 'a') as f:
    #    f.write(exec_cmd('nosetests').strip()+'\n\n')
    for s in source:
        with open('%sdevinfo.txt' % path, 'a') as f:
            if str(s).startswith('racing'):
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
    for s in source:
        with open('%sdevinfo_racing.txt' % path, 'a') as f:
            if not str(s).startswith('racing') or \
                    str(s).startswith('racing/game/'):
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
    for s in source:
        with open('%sdevinfo_game.txt' % path, 'a') as f:
            if not str(s).startswith('racing/game/') or \
                    str(s).startswith('racing/game/thirdparty') or \
                    str(s).startswith('racing/game/tests'):
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
    build_command_str = \
        "tar -czf {out_name} -C {path} devinfo.txt devinfo_racing.txt " + \
        "devinfo_game.txt && rm {path}devinfo.txt " + \
        "{path}devinfo_racing.txt {path}devinfo_game.txt"
    build_command = build_command_str.format(
        path=path, out_name=devinfo_path_str.format(path=path, name=name,
                                                    version=ver_branch))
    system(build_command)
