from os import system
from .build import path, ver_branch, exec_cmd, test_path_str


def build_ut(target, source, env):
    name = env['NAME']
    with open('tests.txt', 'w') as outfile:
        outfile.write(exec_cmd('nosetests'))
    build_command_str = \
        'tar -czf {out_name} tests.txt && rm tests.txt'
    fpath = test_path_str.format(path=path, name=name, version=ver_branch)
    system(build_command_str.format(out_name=fpath))
