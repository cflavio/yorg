from os import system
from setuptools import setup
from setuptools.command.develop import develop


class DevelopPyCommand(develop):

    def run(self):
        develop.run(self)
        system('scons lang=1 images=1 tracks=1')


setup(
    name='Yorg',
    version=0.9,
    cmdclass={'develop': DevelopPyCommand},
    install_requires=[
        'SCons==2.5.0',
        # 'panda3d'  # it doesn't pull the dependency
        ])
