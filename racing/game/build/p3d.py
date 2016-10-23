from os import remove, system, path as os_path
from os.path import dirname, realpath
from shutil import move
from .build import ver, path


def build_p3d(target, source, env):
    name = env['NAME']
    mirr = env['SUPERMIRROR']
    start_dir = os_path.abspath('.') + '/'
    file_path = dirname(realpath(__file__))
    curr_path = dirname(realpath(file_path))
    eng_path = curr_path[len(start_dir):].replace('/', '\/')
    sed_tmpl = "sed -e 's/<version>/{version}/' -e 's/<Name>/{Name}/' " + \
        "-e 's/<name>/{name}/' -e 's/<enginepath>/{eng_path}/' " + \
        "{curr_path}template.pdef > {name}.pdef"
    sed_cmd = sed_tmpl.format(
        version=ver, Name=name.capitalize(), name=name,
        curr_path=file_path + '/', eng_path=eng_path)
    system(sed_cmd)
    if mirr:
        cmd_template = 'panda3d -M {ptools_path} ' + \
            '{ptools_path}/ppackage1.9.p3d -S {ptools_path}/mycert.pem ' + \
            '-i {path} {name}.pdef'
        cmd_str = cmd_template.format(ptools_path=mirr, path=path,
                                      name=name)
    else:
        cmd_str = 'ppackage -i %s %s.pdef' % (path, name)
    system(cmd_str)
    p3d_src_tmpl = '{path}{Name}.{version}.p3d'
    p3d_src = p3d_src_tmpl.format(path=path, Name=name.capitalize(),
                                  version=ver)
    move(p3d_src, env['P3D_PATH'])
    remove(name+'.pdef')
