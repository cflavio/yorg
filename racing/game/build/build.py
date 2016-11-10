from os import path as os_path, walk, chdir, getcwd
from subprocess import Popen, PIPE


def exec_cmd(cmd):
    ret = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True).communicate()
    return '\n'.join(ret)


def __get_branch():
    return exec_cmd('git symbolic-ref HEAD').split('/')[-1].strip()


def __get_version():
    date = exec_cmd('git show -s --format=%ci HEAD')
    return __get_branch()+'-'+date[2:4]+date[5:7]+date[8:10]


def bld_cmd_pref(ptools_path):
    has_super_mirror = os_path.exists(ptools_path)
    bld_cmd_mir_tmpl = 'panda3d -M {ptools} {ptools}/pdeploy1.9.p3d '
    bld_cmd_mir = bld_cmd_mir_tmpl.format(ptools=ptools_path)
    return bld_cmd_mir if has_super_mirror else 'pdeploy '


def bld_cmd(ptools_path):
    return (
        bld_cmd_pref(ptools_path) +
        '-o  {path} {nointernet} -n {name} -N {Name} -v {version} -a ya2.it '
        '-A "Ya2" -l "GPLv3" -L license.txt -e flavio@ya2.it -t width=800 '
        "-t height=600 -P {platform} -i '%s16_png.png' -i '%s32_png.png' "
        "-i '%s48_png.png' -i '%s128_png.png' -i '%s256_png.png' {p3d_path} "
        "installer") % (('assets/images/icon/icon',) * 5)


def image_extensions(files):
    ext = lambda _file: 'png' if _file.endswith('_png.psd') else 'dds'
    return [_file[:_file.rfind('.')+1]+ext(_file) for _file in files]


def set_path(_path):
    global path
    path = _path + ('/' if not _path.endswith('/') else '')
    return path


def get_files(_extensions, exclude_dir=''):
    return [os_path.join(root, filename)
            for root, _, filenames in walk('.')
            for filename in [
                filename
                for filename in filenames
                if any(filename.endswith('.'+ext) for ext in _extensions)]
            if not exclude_dir or exclude_dir not in root.split('/')]


def get_size(start_path='.'):
    return sum(os_path.getsize(os_path.join(dirpath, f))
               for dirpath, dirnames, filenames in walk(start_path)
               for f in filenames)


class InsideDir(object):
    def __init__(self, dir_):
        self.dir = dir_
        self.old_dir = getcwd()

    def __enter__(self):
        chdir(self.dir)

    def __exit__(self, exc_type, exc_val, exc_tb):
        chdir(self.old_dir)


path = 'built/'
try:
    ver_branch = {'master': 'dev', 'stable': 'stable'}[__get_branch()]
except KeyError:
    ver_branch = __get_branch()
ver = __get_version()
p3d_path_str = '{path}{name}-%s.p3d' % ver_branch
win_path_str = '{path}{name}-%s-windows.exe' % ver_branch
osx_path_str = '{path}{name}-%s-osx.zip' % ver_branch
linux_path_str = '{path}{name}-%s-linux_{platform}' % ver_branch
win_path_noint_str = '{path}{name}-%s-nointernet-windows.exe' % ver_branch
osx_path_noint_str = '{path}{name}-%s-nointernet-osx.zip' % ver_branch
linux_path_noint_str = '{path}{name}-%s-nointernet-linux_{platform}' % \
    ver_branch
src_path_str = '{path}{name}-%s-src.tar.gz' % ver_branch
devinfo_path_str = '{path}{name}-%s-devinfo.tar.gz' % ver_branch
test_path_str = '{path}{name}-%s-test.tar.gz' % ver_branch
docs_path_str = '{path}{name}-%s-docs.tar.gz' % ver_branch
pdf_path_str = '{path}{name}-%s-code.tar.gz' % ver_branch
extensions = ['txt', 'ttf', 'dds', 'egg', 'ogg', 'py', 'lua', 'rst', 'pdef',
              'mo']
