from os import system
from setuptools import setup
from setuptools.command.develop import develop
from distutils.cmd import Command
from distutils.log import INFO
from yyagl.build.src import bld_src


class DevelopPyCommand(develop):

    def run(self):
        develop.run(self)
        system('scons lang=1 images=1 tracks=1')


class SourcePkgCommand(Command):

    user_options = []

    def initialize_options(self): pass

    def finalize_options(self): pass

    def run(self):
        self.announce(
            'Building source package',
            level=INFO)
        bld_src(None, None, {'APPNAME': 'yorg'})


if __name__ == '__main__':
    setup(
        name='Yorg',
        version=0.9,
        cmdclass={
            'develop': DevelopPyCommand,
            'source_pkg': SourcePkgCommand},
        install_requires=[
            'SCons==2.5.0',
            # 'panda3d'  # it doesn't pull the dependency
            ])
