from os import system
from setuptools import setup
from setuptools.command.develop import develop
from distutils.cmd import Command
from yyagl.build.build import files
from yyagl.build.src import bld_src
from yyagl.build.devinfo import bld_devinfo


class DevelopPyCmd(develop):

    def run(self):
        develop.run(self)
        system('scons lang=1 images=1 tracks=1')


class AbsCmd(Command):

    env = {'APPNAME': 'yorg'}
    user_options = []

    def initialize_options(self): pass

    def finalize_options(self): pass


class SourcePkgCmd(AbsCmd):

    def run(self): bld_src(None, None, AbsCmd.env)


class DevInfoCmd(AbsCmd):

    def run(self):
        dev_conf = {
            'devinfo': lambda s: str(s).startswith('./yyagl/') or \
                str(s).startswith('./yracing/')}
        AbsCmd.env['DEV_CONF'] = dev_conf
        bld_devinfo(None, files(['py'], ['venv', 'thirdparty']), AbsCmd.env)


if __name__ == '__main__':
    setup(
        name='Yorg',
        version=0.9,
        cmdclass={
            'develop': DevelopPyCmd,
            'source_pkg': SourcePkgCmd,
            'devinfo': DevInfoCmd},
        install_requires=[
            'SCons==2.5.0',
            # 'panda3d'  # it doesn't pull the dependency
            ])
