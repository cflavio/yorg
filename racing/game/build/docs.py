from os import path as os_path, remove, system, walk, chdir, getcwd, \
    makedirs, error
from os.path import expanduser, exists, basename
from shutil import move, rmtree, copytree, copy
from subprocess import Popen, PIPE
from build import ver, has_super_mirror, path, src_path_str, ver_branch, \
    exec_cmd, devinfo_path_str, build_command_str, docs_path_str


def build_docs(target, source, env):
    '''This function creates the documentation using
    `Sphinx <http://sphinx-doc.org>`_ .'''
    name = env['NAME']
    copytree('racing/game/build/docs', path+'docs_apidoc')
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
        "tar -C {path} -czf {out_name} ./docs"
    build_command = build_command_str.format(
        path=path, out_name=docs_path_str.format(path=path, name=name,
                                                 version=ver_branch))
    system(build_command)
    map(rmtree, [path+'docs_apidoc', path+'docs'])
