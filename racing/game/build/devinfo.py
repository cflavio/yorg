from os import path as os_path, remove, system, walk, chdir, getcwd, \
    makedirs, error
from os.path import expanduser, exists, basename
from shutil import move, rmtree, copytree, copy
from subprocess import Popen, PIPE
from build import ver, has_super_mirror, path, src_path_str, ver_branch, \
    exec_cmd, devinfo_path_str


def build_devinfo(target, source, env):
    '''This function creates the
    `pep8 <https://www.python.org/dev/peps/pep-0008>`_,
    `Pylint <http://www.pylint.org>`_ and
    `pyflakes <https://pypi.python.org/pypi/pyflakes>`_ code reports.'''
    name = env['NAME']

    def clean_pylint(pylint_out):
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
        "tar -czf {out_name} -C {path} devinfo.txt && rm {path}devinfo.txt"
    build_command = build_command_str.format(
        path=path, out_name=devinfo_path_str.format(path=path, name=name,
                                                    version=ver_branch))
    system(build_command)
