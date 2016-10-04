'''This module builds the documentation.'''
from os import path as os_path, system
from os.path import dirname, realpath
from shutil import rmtree, copytree
from .build import path, ver_branch, docs_path_str


def build_docs(target, source, env):
    '''This function creates the documentation using
    `Sphinx <http://sphinx-doc.org>`_ .'''
    name = env['NAME']
    curr_path = dirname(realpath(__file__)) + '/'
    copytree(curr_path + 'docs', path+'docs_apidoc')
    cmd = 'sed -i.bak -e "s/<name>/%s/" %sdocs_apidoc/index.rst'
    system(cmd % (name.capitalize(), path))
    curr_path = os_path.abspath('.').replace('/', '\/')
    curr_path = curr_path.replace('\\', '\\\\')
    cmd_tmpl = 'sed -i.bak -e "s/<name>/{name}/" ' + \
        '-e "s/<src_path>/{src_path}/" -e "s/<version>/{version}/" ' + \
        '{path}docs_apidoc/conf.py'
    system(cmd_tmpl.format(
        name=name.capitalize(),
        version=ver_branch,
        path=path,
        src_path=curr_path))
    system('sphinx-apidoc -o %sdocs_apidoc .' % path)
    system("sed -i 1s/./Modules/ %sdocs_apidoc/modules.rst" % path)
    system('sphinx-build -b html %sdocs_apidoc %sdocs' % (path, path))
    build_command_str = 'tar -C {path} -czf {out_name} ./docs'
    f_out = docs_path_str.format(path=path, name=name, version=ver_branch)
    build_command = build_command_str.format(path=path, out_name=f_out)
    system(build_command)
    map(rmtree, [path+'docs_apidoc', path+'docs'])
