'''This module contains all the needed builds: game, documentation
and reports; furthermore it contains all the functions needed by **SCons**.
In this module's functions you will often find *target*, *source* and *env*
arguments. The meaning of these arguments is:
    |  *target*: target files of the builder;
    |  *source*: source files of the builder;
    |  *env*: builder's environment.
More details about *target*, *source* and *env* files
`here <http://www.scons.org/>`_.'''


from os import path as os_path, remove, system, walk, chdir, getcwd, \
    makedirs, error
from os.path import expanduser, exists, basename
from shutil import move, rmtree, copytree, copy
from subprocess import Popen, PIPE


def exec_cmd(cmd):
    '''This function execute the *cmd* command and returns its output.'''
    return '\n'.join(
        Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True).communicate())


def __get_branch():
    return exec_cmd('git symbolic-ref HEAD').split('/')[-1].strip()


def __get_version():
    date = exec_cmd('git show -s --format=%ci HEAD')
    return __get_branch()+'-'+date[2:4]+date[5:7]+date[8:10]


path = 'built/'
ver_branch = {'master': 'stable', 'dev': 'dev'}[__get_branch()]
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

home = expanduser('~')
ptools_path = home+'/runtime_panda3d'
has_super_mirror = os_path.exists(ptools_path)
bld_cmd_mir_tmpl = 'panda3d -M {ptools} {ptools}/pdeploy1.9.p3d '
bld_cmd_mir = bld_cmd_mir_tmpl.format(ptools=ptools_path)

build_command_prefix = bld_cmd_mir if has_super_mirror else 'pdeploy1.9 '
build_command_str = (
    build_command_prefix +
    '-o  {path} {nointernet} -n {name} -N {Name} -v {version} -a ya2.it -A '
    '"Ya2" -l "GPLv3" -L license.txt -e flavio@ya2.it -t width=800 '
    "-t height=600 -P {platform} -i '%s16_png.png' -i '%s32_png.png' "
    "-i '%s48_png.png' -i '%s128_png.png' -i '%s256_png.png' {p3d_path} "
    "installer") % (('assets/images/icon/icon',) * 5)

extensions = ['txt', 'ttf', 'dds', 'egg', 'ogg', 'py', 'lua', 'rst', 'pdef',
              'mo']


def set_path(_path):
    '''This functions sets the output path, that is where to put the builds.'''
    global path
    path = _path + ('/' if not _path.endswith('/') else '')
    return path


def build_p3d(target, source, env):
    '''This function builds the
    `p3d <http://www.panda3d.org/manual/index.php/Introduction_to_p3d_files>`_
    file of the game.'''
    name = env['NAME']
    sed_tmpl = "sed -e 's/<version>/{version}/' -e 's/<Name>/{Name}/' " + \
        "-e 's/<name>/{name}/' ya2/build/template.pdef > {name}.pdef"
    system(sed_tmpl.format(version=ver, Name=name.capitalize(), name=name))
    if has_super_mirror:
        cmd_template = 'panda3d -M {ptools_path} ' + \
            '{ptools_path}/ppackage1.9.p3d -S {ptools_path}/mycert.pem ' + \
            '-i {path} {name}.pdef'
        cmd_str = cmd_template.format(ptools_path=ptools_path, path=path,
                                      name=name)
    else:
        cmd_str = 'ppackage1.9 -i %s %s.pdef' % (path, name)
    system(cmd_str)
    p3d_src_tmpl = '{path}{Name}.{version}.p3d'
    p3d_src = p3d_src_tmpl.format(path=path, Name=name.capitalize(),
                                  version=ver)
    move(p3d_src, env['P3D_PATH'])
    remove(name+'.pdef')


def build_src(target, source, env):
    '''This function creates a tar.gz file with the game sources.'''
    name = env['NAME']
    build_command_str = \
        "tar --transform 's/^./{name}/' -cf {out_name} " +\
        "--exclude '{out_name}' --exclude '.git' --exclude '.kdev4' " +\
        "--exclude '{name}.kdev4' --exclude '.sconsign.dblite' " +\
        "--exclude '*.pyc' --exclude .settings --exclude .project " +\
        "--exclude .pydevproject ."
    build_command = build_command_str.format(
        name=name, out_name=src_path_str.format(path=path, name=name,
                                                version=ver_branch))
    system(build_command)


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
        "tar -cf {out_name} -C {path} devinfo.txt && rm {path}devinfo.txt"
    build_command = build_command_str.format(
        path=path, out_name=devinfo_path_str.format(path=path, name=name,
                                                    version=ver_branch))
    system(build_command)


def build_windows(target, source, env):
    '''This function builds the Windows installer.'''
    name = env['NAME']
    nointernet = '-s' if env['NOINTERNET'] else ''
    int_str = '-nointernet' if env['NOINTERNET'] else ''
    build_command = build_command_str.format(
        path=path, name=name, Name=name.capitalize(), version=ver,
        p3d_path=env['P3D_PATH'], platform='win32', nointernet=nointernet)
    system(build_command)
    win_path = '{path}win32/{Name} {version}.exe'
    win_tgt = '{path}{name}-{version}{int_str}-windows.exe'
    win_path_fmt = win_path.format(path=path, Name=name.capitalize(),
                                   version=ver, int_str=int_str)
    win_tgt_fmt = win_tgt.format(path=path, name=name, version=ver_branch,
                                 int_str=int_str)
    move(win_path_fmt, win_tgt_fmt)
    rmtree('%swin32' % path)


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
    osx_cmd_tmpl = 'cd '+path+'osx_i386 && zip -r ../'+osx_tgt+' '+osx_path +\
                   ' && cd ../..'
    osx_cmd = osx_cmd_tmpl.format(Name=name.capitalize(), name=name,
                                  version=ver_branch, int_str=int_str)
    system(osx_cmd)
    rmtree('%sosx_i386' % path)


def build_linux(target, source, env):
    '''This function builds the Linux installer.'''
    name = env['NAME']
    platform = env['PLATFORM']
    nointernet = '-s' if env['NOINTERNET'] else ''
    int_str = '-nointernet' if env['NOINTERNET'] else ''
    build_command = build_command_str.format(
        path=path, name=name, Name=name.capitalize(), version=ver,
        p3d_path=env['P3D_PATH'], platform='linux_'+platform,
        nointernet=nointernet)
    system(build_command)
    start_dir = os_path.abspath('.') + '/'
    with InsideDir(path+'linux_'+platform):
        makedirs('image/data')
        copytree(start_dir+'ya2/build/mojosetup/meta', 'image/meta')
        copytree(start_dir+'ya2/build/mojosetup/scripts', 'image/scripts')
        copytree(start_dir+'licenses', 'image/data/licenses')
        copy(start_dir+'license.txt', 'image/data/license.txt')
        copy(start_dir+'ya2/build/mojosetup/mojosetup_'+platform, '.')
        if os_path.exists(start_dir+'ya2/build/mojosetup/guis'):
            makedirs('image/guis')
            copy(start_dir+'ya2/build/mojosetup/guis/%s/'
                 'libmojosetupgui_gtkplus2.so' % platform,
                 'image/guis/libmojosetupgui_gtkplus2.so')
        arch_dict = {'i386': 'i686', 'amd64': 'x86_64'}
        system('tar -zxvf %s-%s-1-%s.pkg.tar.gz' % (name, ver,
                                                    arch_dict[platform]))
        remove('.PKGINFO')
        move('usr/bin/'+name, 'image/data/'+name)
        copy(start_dir+'assets/images/icon/icon48_png.png',
             'image/data/icon.png')
        system("sed -i.bak -e 's/<version>/{version}/' "
               "-e 's/<size>/{size}/' -e 's/<name>/{name}/' "
               "-e 's/<Name>/{Name}/' image/scripts/config.lua".format(
                   version=ver_branch, size=get_size('image'), name=name,
                   Name=name.capitalize()))
        if nointernet:
            copytree('usr/lib/'+name, 'image/data/lib')
            linux_exe_cmd = (
                build_command_prefix +
                '-o  . {nointernet} -t host_dir=./lib -t verify_contents=never '
                '-n {name} -N {Name} -v {version} -a ya2.it -A "Ya2" '
                '-l "GPLv3" -L license.txt -e flavio@ya2.it -t width=800 '
                "-t height=600 -P {platform} -i '%s16_png.png' "
                "-i '%s32_png.png' -i '%s48_png.png' -i '%s128_png.png' "
                "-i '%s256_png.png' ../{p3d_path} standalone") % (
                    ('assets/images/icon/icon',) * 5)
            build_command = linux_exe_cmd.format(
                path=path, name=name, Name=name.capitalize(), version=ver,
                p3d_path=basename(env['P3D_PATH']), platform='linux_'+platform,
                nointernet=nointernet)
            system(build_command)
            move('linux_'+platform+'/'+name, 'image/data/'+name)
        with InsideDir('image'):
            system('zip -9r ../pdata.zip *')
        system('cat pdata.zip >> ./mojosetup_'+platform)
        move('mojosetup_'+platform,
             '%s-%s%s-linux_%s' % (name, ver_branch, int_str, platform))
        system('chmod +x %s-%s%s-linux_%s' % (name, ver_branch, int_str,
                                              platform))
        move('%s-%s%s-linux_%s' % (name, ver_branch, int_str, platform),
             '../%s-%s%s-linux_%s' % (name, ver_branch, int_str, platform))
    rmtree(path+'linux_'+platform)


def build_docs(target, source, env):
    '''This function creates the documentation using
    `Sphinx <http://sphinx-doc.org>`_ .'''
    name = env['NAME']
    copytree('ya2/build/docs', path+'docs_apidoc')
    system('sed -i.bak -e "s/<name>/%s/" %sdocs_apidoc/index.rst'
           % (name.capitalize(), path))
    curr_path = os_path.abspath('.').replace('/', '\/')
    curr_path = curr_path.replace('\\', '\\\\')
    system('sed -i.bak -e "s/<name>/{name}/" -e "s/<src_path>/{src_path}/" '
           '-e "s/<version>/{version}/" {path}docs_apidoc/conf.py'.format(
                name=name.capitalize(), version=ver_branch, path=path,
                src_path=curr_path))
    system('sphinx-apidoc -o %sdocs_apidoc .' % path)
    system("sed -i 1s/./Modules/ %sdocs_apidoc/modules.rst" % path)
    system('sphinx-build -b html %sdocs_apidoc %sdocs' % (path, path))
    build_command_str = \
        "tar -C {path} -cf {out_name} ./docs"
    build_command = build_command_str.format(
        path=path, out_name=docs_path_str.format(path=path, name=name,
                                                 version=ver_branch))
    system(build_command)
    map(rmtree, [path+'docs_apidoc', path+'docs'])


def build_string_template(target, source, env):
    '''This function creates the *gettext* templates (to manage localization)
    merging with the already translated ones.'''
    name = env['NAME']
    lang = env['LANG']
    src_files = ' '.join(get_files(['py']))
    cmd_tmpl = 'xgettext -d {name} -L python -o {name}.pot '
    system(cmd_tmpl.format(name=name) + src_files)
    try:
        makedirs(lang+'it_IT/LC_MESSAGES')
    except error:
        pass
    move(name+'.pot', lang+'it_IT/LC_MESSAGES/%s.pot' % name)
    p = lang+'it_IT/LC_MESSAGES/'
    for a in ['CHARSET/UTF-8', 'ENCODING/8bit']:
        cmd_tmpl = "sed 's/{src}/' {path}{name}.pot > {path}{name}tmp.po"
        system(cmd_tmpl.format(src=a, path=p, name=name))
        move(p+name+'tmp.po', p+name+'.pot')
    if not exists(p+name+'.po'):
        copy(p+name+'.pot', p+name+'.po')
    cmd_str = 'msgmerge -o {path}{name}merge.po {path}{name}.po '+\
        '{path}{name}.pot'
    system(cmd_str.format(path=p, name=name))
    copy(p+name+'merge.po', p+name+'.po')
    lines = open(p+name+'.po', 'r').readlines()
    with open(p+name+'.po', 'w') as f:
        for l in lines:
            f.write('"POT-Creation-Date: YEAR-MO-DA HO:MI+ZONE\\n"\n'
                    if l.startswith('"POT-Creation-Date: ') else l)


def build_strings(target, source, env):
    '''This function creates the *mo* files (binaries) containing the
    translated strings that would be used in the game, starting from
    the *po* files.'''
    name = env['NAME']
    lang = env['LANG']
    p = lang+'it_IT/LC_MESSAGES/'
    system('msgfmt -o {path}{name}.mo {path}{name}.po'.format(path=p,
                                                              name=name))


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


def image_extensions(files):
    ext = lambda _file: 'png' if _file.endswith('_png.psd') else 'dds'
    return [_file[:_file.rfind('.')+1]+ext(_file) for _file in files]


def build_images(target, source, env):

    def get_img_fmt(_file):
        cmd = 'identify -verbose "%s" | grep alpha' % _file
        alpha = exec_cmd(cmd).strip()
        geometry = exec_cmd('identify -verbose "%s" | grep Geometry' % _file)
        split_dim = lambda geom: geom.split()[1].split('+')[0].split('x')
        size = [int(dim) for dim in split_dim(geometry)]
        return alpha, size

    for _file in [str(src) for src in source]:
        png = _file[:-3]+'png'
        alpha, size = get_img_fmt(_file)
        sizes = [2**i for i in range(0, 12)]
        low_pow = lambda x: max([y for y in sizes if y <= x])
        width, height = map(low_pow, size)
        cmd = 'convert "%s"[0] -resize %dx%d! "%s"' % (_file, width, height,
                                                       png)
        system(cmd)
        if not png.endswith('_png.png'):
            cmd = 'nvcompress -bc3 '+('-alpha' if alpha else '')+' -nomips "'+\
                png+'" "'+_file[:-3]+'dds"'
            system(cmd)
            remove(png)


def build_pdf(target, source, env):
    name = env['NAME']
    cmd = "enscript --font=Courier11 --continuous-page-numbers " + \
        "--pretty-print=python -o - `find . -name '*.py'` | " + \
        "ps2pdf - sources.pdf ; pdfnup --nup 2x1 -o sources.pdf sources.pdf"
    system(cmd)
    cmd = 'tar -cf {out_name} sources.pdf && rm sources.pdf'
    cmd = cmd.format(
        out_name=pdf_path_str.format(path=path, name=name, version=ver_branch))
    system(cmd)


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
