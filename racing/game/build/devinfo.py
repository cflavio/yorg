'''Builds info for developers.'''
from os import system
from .build import path, ver_branch, exec_cmd, devinfo_path_str


def build_devinfo(target, source, env):
    '''This function creates the
    `pep8 <https://www.python.org/dev/peps/pep-0008>`_,
    `Pylint <http://www.pylint.org>`_ and
    `pyflakes <https://pypi.python.org/pypi/pyflakes>`_ code reports.'''
    name = env['NAME']
    dev_conf = env['DEV_CONF']

    def clean_pylint(pylint_out):
        '''Cleans pylint stuff.'''
        clean_out = ''
        skipping = False
        err_str = 'No config file found, using default configuration'
        lines = [line for line in pylint_out.split('\n') if line != err_str]
        for line in lines:
            if line == 'Traceback (most recent call last):':
                skipping = True
            elif line == 'RuntimeError: maximum recursion depth ' +\
                         'exceeded while calling a Python object':
                skipping = False
            elif not skipping:
                clean_out += line + '\n'
        return clean_out

    def append_file(src, cond, outfile):
        '''Appends a file.'''
        if cond(src):
            return
        outfile.write('    '+str(src)+'\n')
        outs = [clean_pylint((exec_cmd('pylint -r n '+str(src)))),
                exec_cmd('pyflakes '+str(src)),
                exec_cmd('pep8 '+str(src))]
        outs = [out.strip() for out in outs]
        for out in [out for out in outs if out]:
            outfile.write(out+'\n')
        outfile.write('\n')

    def process(name, cond):
        '''Processes files which don't satisfy cond.'''
        for src in source:
            with open(name % path, 'a') as outfile:
                append_file(src, cond, outfile)

    for fname, cond in dev_conf.items():
        process('%s' + fname + '.txt', cond)
    names, rmnames = '', ''
    for fname in dev_conf:
        names += fname + '.txt '
        rmnames += '{path}' + fname + '.txt '

    build_command_str = \
        'tar -czf {out_name} -C {path} ' + names + ' && rm ' + rmnames
    fpath = devinfo_path_str.format(path=path, name=name, version=ver_branch)
    build_command = build_command_str.format(path=path, out_name=fpath)
    system(build_command)
