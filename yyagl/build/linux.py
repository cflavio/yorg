from os import path as os_path, remove, system, makedirs
from os.path import basename, dirname, realpath
from shutil import move, rmtree, copytree, copy
from .build import ver, path, ver_branch, InsideDir, get_size, bld_cmd_pref, \
    bld_cmd


def __prepare_folders(start_dir, platform):
    makedirs('image/data')
    curr_path = dirname(realpath(__file__)) + '/'
    copytree(curr_path + 'mojosetup/meta', 'image/meta')
    copytree(curr_path + 'mojosetup/scripts', 'image/scripts')
    copytree(curr_path + '../licenses', 'image/data/licenses')
    copy(start_dir + 'license.txt', 'image/data/license.txt')
    copy(curr_path + 'mojosetup/mojosetup_' + platform, '.')
    if not os_path.exists(curr_path + 'mojosetup/guis'):
        return
    makedirs('image/guis')
    libpath = curr_path + 'mojosetup/guis/%s/libmojosetupgui_gtkplus2.so'
    dst_path = 'image/guis/libmojosetupgui_gtkplus2.so'
    copy(start_dir + libpath % platform, dst_path)


def __build(name, start_dir, platform, ico_file):
    arch_dict = {'i386': 'i686', 'amd64': 'x86_64'}
    cmd_tmpl = 'tar -zxvf %s-%s-1-%s.pkg.tar.gz'
    system(cmd_tmpl % (name, ver, arch_dict[platform]))
    remove('.PKGINFO')
    move('usr/bin/' + name, 'image/data/' + name)
    copy(start_dir + ico_file % '48', 'image/data/icon.png')
    cmd_tmpl = "sed -i.bak -e 's/<version>/{version}/' " + \
        "-e 's/<size>/{size}/' -e 's/<name>/{name}/' " + \
        "-e 's/<Name>/{Name}/' image/scripts/config.lua"
    cmd = cmd_tmpl.format(version=ver_branch, size=get_size('image'),
                          name=name, Name=name.capitalize())
    system(cmd)


def __build_no_internet(name, platform, ico_file, p3d_path, nointernet, mirr):
    copytree('usr/lib/'+name, 'image/data/lib')
    cmd_tmpl = bld_cmd_pref(mirr) + \
        '-o  . {nointernet} -t host_dir=./lib ' + \
        '-t verify_contents=never ' + \
        '-n {name} -N {Name} -v {version} -a ya2.it -A "Ya2" ' + \
        '-l "GPLv3" -L license.txt -e flavio@ya2.it -t width=800 ' + \
        "-t height=600 -P {platform} {icons} ../{p3d_path} standalone"
    dims = ['16', '32', '48', '128', '256']
    ico_str = ''.join(["-i '" + ico_file % dim + "' " for dim in dims])
    build_command = cmd_tmpl.format(
        path=path, name=name, Name=name.capitalize(), version=ver,
        p3d_path=basename(p3d_path), platform='linux_'+platform,
        nointernet=nointernet, icons=ico_str)
    system(build_command)
    move('linux_' + platform + '/' + name, 'image/data/' + name)


def __build_packages(name, platform, int_str):
    with InsideDir('image'):
        system('zip -9r ../pdata.zip *')
    system('cat pdata.zip >> ./mojosetup_' + platform)
    dst = '%s-%s%s-linux_%s' % (name, ver_branch, int_str, platform)
    move('mojosetup_' + platform, dst)
    cmd = 'chmod +x %s-%s%s-linux_%s' % (name, ver_branch, int_str, platform)
    system(cmd)
    src = '%s-%s%s-linux_%s' % (name, ver_branch, int_str, platform)
    dst = '../%s-%s%s-linux_%s' % (name, ver_branch, int_str, platform)
    move(src, dst)


def build_linux(target, source, env):
    name = env['NAME']
    platform = env['PLATFORM']
    ico_file = env['ICO_FILE']
    mirr = env['SUPERMIRROR']
    nointernet = '-s' if env['NOINTERNET'] else ''
    int_str = '-nointernet' if env['NOINTERNET'] else ''
    build_command = bld_cmd(mirr).format(
        path=path, name=name, Name=name.capitalize(), version=ver,
        p3d_path=env['P3D_PATH'], platform='linux_'+platform,
        nointernet=nointernet)
    system(build_command)
    start_dir = os_path.abspath('.') + '/'
    with InsideDir(path + 'linux_' + platform):
        __prepare_folders(start_dir, platform)
        __build(name, start_dir, platform, ico_file)
        if nointernet:
            args = name, platform, ico_file, env['P3D_PATH'], nointernet, mirr
            __build_no_internet(*args)
        __build_packages(name, platform, int_str)
    rmtree(path+'linux_'+platform)
