'''P3D build.'''
from os import remove, system
from shutil import move
from .build import ver, has_super_mirror, path, ptools_path


def build_p3d(target, source, env):
    '''This function builds the
    `p3d <http://www.panda3d.org/manual/index.php/Introduction_to_p3d_files>`_
    file of the game.'''
    name = env['NAME']
    sed_tmpl = "sed -e 's/<version>/{version}/' -e 's/<Name>/{Name}/' " + \
        "-e 's/<name>/{name}/' racing/game/build/template.pdef > {name}.pdef"
    system(sed_tmpl.format(version=ver, Name=name.capitalize(), name=name))
    if has_super_mirror:
        cmd_template = 'panda3d -M {ptools_path} ' + \
            '{ptools_path}/ppackage1.9.p3d -S {ptools_path}/mycert.pem ' + \
            '-i {path} {name}.pdef'
        cmd_str = cmd_template.format(ptools_path=ptools_path, path=path,
                                      name=name)
    else:
        cmd_str = 'ppackage -i %s %s.pdef' % (path, name)
    system(cmd_str)
    p3d_src_tmpl = '{path}{Name}.{version}.p3d'
    p3d_src = p3d_src_tmpl.format(path=path, Name=name.capitalize(),
                                  version=ver)
    move(p3d_src, env['P3D_PATH'])
    remove(name+'.pdef')
