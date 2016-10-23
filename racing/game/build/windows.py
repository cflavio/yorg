from os import system
from shutil import move, rmtree
from .build import ver, path, ver_branch, bld_cmd


def build_windows(target, source, env):
    name = env['NAME']
    mirr = env['SUPERMIRROR']
    nointernet = '-s' if env['NOINTERNET'] else ''
    int_str = '-nointernet' if env['NOINTERNET'] else ''
    build_command = bld_cmd(mirr).format(
        path=path, name=name, Name=name.capitalize(), version=ver,
        p3d_path=env['P3D_PATH'], platform='win_i386', nointernet=nointernet)
    system(build_command)
    win_path = '{path}win_i386/{Name} {version}.exe'
    win_tgt = '{path}{name}-{version}{int_str}-windows.exe'
    win_path_fmt = win_path.format(
        path=path, Name=name.capitalize(), version=ver, int_str=int_str)
    win_tgt_fmt = win_tgt.format(
        path=path, name=name, version=ver_branch, int_str=int_str)
    move(win_path_fmt, win_tgt_fmt)
    rmtree('%swin_i386' % path)
