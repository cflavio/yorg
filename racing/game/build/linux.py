'''Linux build.'''
from os import path as os_path, remove, system, makedirs
from os.path import basename
from shutil import move, rmtree, copytree, copy
from .build import ver, path, ver_branch, build_command_str, InsideDir, \
    build_command_prefix, get_size


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
    with InsideDir(path + 'linux_' + platform):
        makedirs('image/data')
        copytree(start_dir + 'racing/game/build/mojosetup/meta', 'image/meta')
        src_dir = start_dir + 'racing/game/build/mojosetup/scripts'
        copytree(src_dir, 'image/scripts')
        copytree(start_dir + 'racing/game/licenses', 'image/data/licenses')
        copy(start_dir + 'license.txt', 'image/data/license.txt')
        src = start_dir + 'racing/game/build/mojosetup/mojosetup_' + platform
        copy(src, '.')
        if os_path.exists(start_dir + 'racing/game/build/mojosetup/guis'):
            makedirs('image/guis')
            libpath = 'racing/game/build/mojosetup/guis/%s/' + \
                'libmojosetupgui_gtkplus2.so'
            dst_path = 'image/guis/libmojosetupgui_gtkplus2.so'
            copy(start_dir + libpath % platform, dst_path)
        arch_dict = {'i386': 'i686', 'amd64': 'x86_64'}
        cmd_tmpl = 'tar -zxvf %s-%s-1-%s.pkg.tar.gz'
        system(cmd_tmpl % (name, ver, arch_dict[platform]))
        remove('.PKGINFO')
        move('usr/bin/'+name, 'image/data/'+name)
        src_path = start_dir + 'assets/images/icon/icon48_png.png'
        copy(src_path, 'image/data/icon.png')
        cmd_tmpl = "sed -i.bak -e 's/<version>/{version}/' " + \
            "-e 's/<size>/{size}/' -e 's/<name>/{name}/' " + \
            "-e 's/<Name>/{Name}/' image/scripts/config.lua"
        cmd = cmd_tmpl.format(version=ver_branch, size=get_size('image'),
                              name=name, Name=name.capitalize())
        system(cmd)
        if nointernet:
            copytree('usr/lib/'+name, 'image/data/lib')
            cmd_tmpl = build_command_prefix + \
                '-o  . {nointernet} -t host_dir=./lib ' + \
                '-t verify_contents=never ' + \
                '-n {name} -N {Name} -v {version} -a ya2.it -A "Ya2" ' + \
                '-l "GPLv3" -L license.txt -e flavio@ya2.it -t width=800 ' + \
                "-t height=600 -P {platform} -i '%s16_png.png' " + \
                "-i '%s32_png.png' -i '%s48_png.png' -i '%s128_png.png' " + \
                "-i '%s256_png.png' ../{p3d_path} standalone"
            linux_exe_cmd = cmd_tmpl % (('assets/images/icon/icon',) * 5)
            build_command = linux_exe_cmd.format(
                path=path, name=name, Name=name.capitalize(), version=ver,
                p3d_path=basename(env['P3D_PATH']), platform='linux_'+platform,
                nointernet=nointernet)
            system(build_command)
            move('linux_' + platform + '/' + name, 'image/data/' + name)
        with InsideDir('image'):
            system('zip -9r ../pdata.zip *')
        system('cat pdata.zip >> ./mojosetup_' + platform)
        dst = '%s-%s%s-linux_%s' % (name, ver_branch, int_str, platform)
        move('mojosetup_' + platform, dst)
        cmd_tmpl = 'chmod +x %s-%s%s-linux_%s'
        cmd = cmd_tmpl % (name, ver_branch, int_str, platform)
        system(cmd)
        src = '%s-%s%s-linux_%s' % (name, ver_branch, int_str, platform)
        dst = '../%s-%s%s-linux_%s' % (name, ver_branch, int_str, platform)
        move(src, dst)
    rmtree(path+'linux_'+platform)
