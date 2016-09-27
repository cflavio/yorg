from os import path as os_path, remove, system, walk, chdir, getcwd, \
    makedirs, error
from os.path import expanduser, exists, basename
from shutil import move, rmtree, copytree, copy
from subprocess import Popen, PIPE
from build import ver, has_super_mirror, path, src_path_str, ver_branch, \
    exec_cmd, devinfo_path_str, build_command_str


def build_windows(target, source, env):
    '''This function builds the Windows installer.'''
    name = env['NAME']
    nointernet = '-s' if env['NOINTERNET'] else ''
    int_str = '-nointernet' if env['NOINTERNET'] else ''
    build_command = build_command_str.format(
        path=path, name=name, Name=name.capitalize(), version=ver,
        p3d_path=env['P3D_PATH'], platform='win_i386', nointernet=nointernet)
    system(build_command)
    win_path = '{path}win_i386/{Name} {version}.exe'
    win_tgt = '{path}{name}-{version}{int_str}-windows.exe'
    win_path_fmt = win_path.format(path=path, Name=name.capitalize(),
                                   version=ver, int_str=int_str)
    win_tgt_fmt = win_tgt.format(path=path, name=name, version=ver_branch,
                                 int_str=int_str)
    move(win_path_fmt, win_tgt_fmt)
    rmtree('%swin_i386' % path)
