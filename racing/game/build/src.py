'''Builds a source package.'''
from os import system
from .build import src_path_str, ver_branch, path


def build_src(target, source, env):
    '''This function creates a tar.gz file with the game sources.'''
    name = env['NAME']
    build_command_str = \
        "tar --transform 's/^./{name}/' -czf {out_name} " + \
        "--exclude '{out_name}' --exclude 'built' --exclude '.git' " + \
        "--exclude '.kdev4' " + \
        "--exclude '{name}.kdev4' --exclude '.sconsign.dblite' " + \
        "--exclude '*.pyc' --exclude .settings --exclude .project " + \
        "--exclude .pydevproject --exclude '{name}.geany' ."
    build_command = build_command_str.format(
        name=name, out_name=src_path_str.format(path=path, name=name,
                                                version=ver_branch))
    system(build_command)
