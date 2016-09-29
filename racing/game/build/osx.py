'''OSX build.'''
from os import system
from shutil import rmtree
from .build import ver, path, ver_branch, build_command_str


def build_osx(target, source, env):
    '''This function builds the OSX installer.'''
    name = env['NAME']
    nointernet = '-s' if env['NOINTERNET'] else ''
    int_str = '-nointernet' if env['NOINTERNET'] else ''
    build_command = build_command_str.format(
        path=path, name=name, Name=name.capitalize(), version=ver,
        p3d_path=env['P3D_PATH'], platform='osx_i386', nointernet=nointernet)
    system(build_command)
    osx_path = '{Name}.app'
    osx_tgt = '{name}-{version}{int_str}-osx.zip'
    osx_cmd_tmpl = 'cd ' + path + 'osx_i386 && zip -r ../' + osx_tgt + ' ' + \
        osx_path + ' && cd ../..'
    osx_cmd = osx_cmd_tmpl.format(Name=name.capitalize(), name=name,
                                  version=ver_branch, int_str=int_str)
    system(osx_cmd)
    rmtree('%sosx_i386' % path)
