'''This module contains all the needed builds: game, documentation
and reports; furthermore it contains all the functions needed by **SCons**.
In this module's functions you will often find *target*, *source* and *env*
arguments. The meaning of these arguments is:
    |  *target*: target files of the builder;
    |  *source*: source files of the builder;
    |  *env*: builder's environment.
More details about *target*, *source* and *env* files
`here <http://www.scons.org/>`_.'''


from os import path as os_path, walk, chdir, getcwd
from subprocess import Popen, PIPE


def exec_cmd(cmd):
    '''This function execute the *cmd* command and returns its output.'''
    return '\n'.join(
        Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True).communicate())


def __get_branch():
    '''The current branch.'''
    return exec_cmd('git symbolic-ref HEAD').split('/')[-1].strip()


def __get_version():
    '''The current version.'''
    date = exec_cmd('git show -s --format=%ci HEAD')
    return __get_branch()+'-'+date[2:4]+date[5:7]+date[8:10]


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
devinfo_path_str = '{path}{name}-%s-devinfo.tar.gz' % ver_branch
docs_path_str = '{path}{name}-%s-docs.tar.gz' % ver_branch
pdf_path_str = '{path}{name}-%s-code.tar.gz' % ver_branch

home = '/home/flavio'  # expanduser('~') TODO: don't hardcode that
ptools_path = home+'/runtime_panda3d'
has_super_mirror = os_path.exists(ptools_path)
bld_cmd_mir_tmpl = 'panda3d -M {ptools} {ptools}/pdeploy1.9.p3d '
bld_cmd_mir = bld_cmd_mir_tmpl.format(ptools=ptools_path)

build_command_prefix = bld_cmd_mir if has_super_mirror else 'pdeploy '
build_command_str = (
    build_command_prefix +
    '-o  {path} {nointernet} -n {name} -N {Name} -v {version} -a ya2.it -A '
    '"Ya2" -l "GPLv3" -L license.txt -e flavio@ya2.it -t width=800 '
    "-t height=600 -P {platform} -i '%s16_png.png' -i '%s32_png.png' "
    "-i '%s48_png.png' -i '%s128_png.png' -i '%s256_png.png' {p3d_path} "
    "installer") % (('assets/images/icon/icon',) * 5)


extensions = ['txt', 'ttf', 'dds', 'egg', 'ogg', 'py', 'lua', 'rst', 'pdef',
              'mo']


def image_extensions(files):
    '''The list of image extesions.'''
    ext = lambda _file: 'png' if _file.endswith('_png.psd') else 'dds'
    return [_file[:_file.rfind('.')+1]+ext(_file) for _file in files]


def set_path(_path):
    '''This functions sets the output path, that is where to put the builds.'''
    global path
    path = _path + ('/' if not _path.endswith('/') else '')
    return path


def get_files(extensions, exclude_dir=''):
    '''This function returns the list of all files in the current directory
    (and not in the *exclude_dir* directory) and whose name ends with an
    extension in the *extensions* list.'''
    return [os_path.join(root, filename)
            for root, dirnames, filenames in walk('.')
            for filename in [
                filename
                for filename in filenames
                if any(filename.endswith('.'+ext) for ext in extensions)]
            if not exclude_dir or exclude_dir not in root.split('/')]


def get_size(start_path='.'):
    '''This function returns the size in bytes of the *start_path* dir.'''
    return sum(os_path.getsize(os_path.join(dirpath, f))
               for dirpath, dirnames, filenames in walk(start_path)
               for f in filenames)


class InsideDir(object):
    '''This class is a context manager; it executes a code block
    within a specific folder.'''
    def __init__(self, dir_):
        self.dir = dir_
        self.old_dir = getcwd()

    def __enter__(self):
        chdir(self.dir)

    def __exit__(self, exc_type, exc_val, exc_tb):
        chdir(self.old_dir)
