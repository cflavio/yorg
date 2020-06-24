# usage: python setup.py models --cores=1

from os import system, getcwd, chdir
from sys import argv
from collections import namedtuple
from distutils.cmd import Command
from direct.dist.commands import bdist_apps
from shutil import rmtree
from setuptools import setup
from setuptools.command.develop import develop
from yyagl.build.build import branch, files, ver
from yyagl.build.src import bld_src
from yyagl.build.devinfo import bld_devinfo
from yyagl.build.docs import bld_docs
from yyagl.build.pdf import bld_pdfs
from yyagl.build.uml import bld_uml
from yyagl.build.imgs import bld_images
from yyagl.build.tracks import bld_models
from yyagl.build.strings import bld_mo, bld_pot, bld_merge
from yyagl.build.linux import bld_linux
from yyagl.build.windows import bld_windows
from yyagl.build.appimage import bld_appimage
from yyagl.build.flatpak import bld_flatpak
from yyagl.build.snap import bld_snap


msg = '''NOTE: please be sure that you've already created the assets with:
    * python setup.py images models lang'''


class DevelopPyCmd(develop):

    def run(self):
        develop.run(self)
        system('scons lang=1 images=1 tracks=1')


class AbsCmd(Command):

    env = {'APPNAME': 'yorg'}
    user_options = [('cores=', None, '#cores')]

    def initialize_options(self): self.cores = 0

    def finalize_options(self): AbsCmd.env['CORES'] = int(self.cores)


class SourcePkgCmd(AbsCmd):

    def run(self): bld_src(None, None, AbsCmd.env)


class DevInfoCmd(AbsCmd):

    def run(self):
        dev_conf = {
            'devinfo': lambda s: str(s).startswith('./yyagl/') or
            str(s).startswith('./yracing/')}
        AbsCmd.env['DEV_CONF'] = dev_conf
        bld_devinfo(None, files(['py'], ['venv', 'thirdparty']), AbsCmd.env)


class DocsCmd(AbsCmd):

    def run(self):
        AbsCmd.env['DOCS_PATH'] = getcwd()
        bld_docs(None, None, AbsCmd.env)


class PDFCmd(AbsCmd):

    def run(self):
        PDFInfo = namedtuple('PDFInfo', 'lng root fil excl')
        filt_game = ['./yyagl/racing/*', './yyagl/thirdparty/*']
        yorg_fil_dirs = ['yyagl', 'menu', 'yorg', 'licenses', 'assets', 'venv',
                         'build', 'built', 'yracing']
        yorg_fil = ['./%s/*' % dname for dname in yorg_fil_dirs]
        yorg_fil += ['./yorg_error.txt']
        yorg_lst = [
            PDFInfo('python', './yorg', '*.py', []),
            PDFInfo('python', '.', '*.py SConstruct *.md *.txt', yorg_fil)]
        racing_fil = ['./yyagl/racing/game/*', './yyagl/racing/car/*',
                      './yyagl/racing/race/*', './yyagl/racing/track/*']
        # racing_lst = [PDFInfo('python', './yyagl/racing', '*.py',
        #                       racing_fil)]
        yyagl_fil = ['./yyagl/build/*', './yyagl/engine/*', './yyagl/lib/*',
                     './yyagl/tests/*']
        # yyagl_lst = [
        #     PDFInfo('python', './yyagl', '*.py *.pdef',
        #             filt_game + yyagl_fil),
        #     PDFInfo('c', './yyagl', '*.vert *.frag', filt_game + yyagl_fil)]
        binfo_lst = [
            ('python', '*.py *.pdef'), ('lua', 'config.lua'),
            ('', '*.rst *.css_t *.conf'), ('html', '*.html'),
            ('javascript', '*.js')]
        # build_lst = [PDFInfo(binfo[0], './yyagl/build', binfo[1], filt_game)
        #              for binfo in binfo_lst]
        pdf_conf = {
            'yorg_menu': [PDFInfo('python', './menu', '*.py', [])],
            'yorg': yorg_lst}
        AbsCmd.env['PDF_CONF'] = pdf_conf
        bld_pdfs(None, None, AbsCmd.env)


class ImagesCmd(AbsCmd):

    def run(self):
        bld_images(
            None, files(['jpg', 'png'], ['tex'], ['_png.png']), AbsCmd.env)


class UMLCmd(AbsCmd):

    def run(self):
        AbsCmd.env['UML_FILTER'] = ['yyagl', 'yracing']
        bld_uml(None, None, AbsCmd.env)


class ModelsCmd(AbsCmd):

    def run(self):
        AbsCmd.env['MODELS_DIR_PATH'] = 'assets/models'
        AbsCmd.env['CARS_DIR_PATH'] = 'assets/cars'
        AbsCmd.env['TRACKS_DIR_PATH'] = 'assets/tracks'
        bld_models(None, None, AbsCmd.env)
        print('ModelsCmd: done')


class LangCmd(AbsCmd):

    lang_path = 'assets/locale/'

    def _process_lang(self, lang_code):
        lang_name = 'assets/po/%s.po' % lang_code
        bld_merge(lang_name, None, AbsCmd.env)
        lang_mo = self.lang_path + lang_code + \
            '/LC_MESSAGES/%s.mo' % AbsCmd.env['APPNAME']
        bld_mo(lang_mo, None, AbsCmd.env)

    def run(self):
        AbsCmd.env['LNG'] = self.lang_path
        bld_pot(None, None, AbsCmd.env)
        list(map(self._process_lang,
                 ['it_IT', 'de_DE', 'gd', 'es_ES', 'gl_ES', 'fr_FR']))


class AppImageCmd(AbsCmd):

    def run(self):
        print(msg)
        AbsCmd.env['ICO_FPATH'] = 'assets/images/icon/icon%s_png.png'
        bld_appimage(None, None, AbsCmd.env)


class FlatPakCmd(AbsCmd):

    def run(self):
        print(msg)
        AbsCmd.env['ICO_FPATH'] = 'assets/images/icon/icon%s_png.png'
        AbsCmd.env['FLATPAK_DST'] = getcwd() + '/built'
        bld_flatpak(None, None, AbsCmd.env)


class SnapCmd(AbsCmd):

    def run(self):
        print(msg)
        AbsCmd.env['ICO_FPATH'] = 'assets/images/icon/icon%s_png.png'
        summary = 'Yorg is an Open source Racing Game'
        desc = "Yorg (Yorg's an Open Racing Game) is a free open source " + \
               "racing game developed by Ya2 using Panda3D for Windows, " + \
               "OSX and Linux."
        _branch = branch
        bld_snap(None, None, AbsCmd.env, ver.split('-')[0], _branch, summary,
                 desc)


class BDistAppsCmd(bdist_apps):

    # e.g. python setup.py bdist_apps --nowin=1

    user_options = bdist_apps.user_options + [
        ('cores', None, '#cores'),
        ('nowin=', None, "don't build for windows"),
        ('nolinux=', None, "don't build for linux")
    ]

    def initialize_options(self):
        bdist_apps.initialize_options(self)
        self.nowin = None
        self.nolinux = None

    def finalize_options(self):
        bdist_apps.finalize_options(self)

    def run(self):
        print(msg)
        bdist_apps.run(self)
        chdir('..')
        if not self.nowin:
            bld_windows(None, None, AbsCmd.env)
        AbsCmd.env['ICO_FPATH'] = 'assets/images/icon/icon%s_png.png'
        if not self.nolinux:
            bld_linux(None, None, AbsCmd.env)
        #rmtree('build')
        #rmtree('dist')


if __name__ == '__main__':
    platform_lst = []
    installers_dct = {}
    if all('--nowin' not in arg for arg in argv):
        platform_lst += ['win_amd64']
        installers_dct['win_amd64'] = ['xztar', 'nsis']
    if all('--nolinux' not in arg for arg in argv):
        platform_lst += ['manylinux1_x86_64']
        installers_dct['manylinux1_x86_64'] = ['xztar']
    appname = AbsCmd.env['APPNAME']
    setup(
        name=appname,
        version=branch,
        cmdclass={
            'develop': DevelopPyCmd,
            'source_pkg': SourcePkgCmd,
            'devinfo': DevInfoCmd,
            'docs': DocsCmd,
            'pdf': PDFCmd,
            'uml': UMLCmd,
            'images': ImagesCmd,
            'models': ModelsCmd,
            'lang': LangCmd,
            'appimage': AppImageCmd,
            'flatpak': FlatPakCmd,
            'snap': SnapCmd,
            'bdist_apps': BDistAppsCmd},
        install_requires=[
            # 'SCons==2.5.0',
            # 'panda3d'  # it doesn't pull the dependency
            ],
        options={
            'build_apps': {
                'exclude_patterns': [
                    'build/*', 'built/*', 'setup.py', 'requirements.txt',
                    '*.swp', 'SConstruct', 'venv/*', '.git*', '*.pyc',
                    'options.json', '__pycache__'],
                'log_filename': '$USER_APPDATA/Yorg/p3d_log.log',
                'plugins': ['pandagl', 'p3openal_audio'],
                'gui_apps': {appname: 'main.py'},
                'icons': {
                    appname: [
                        'assets/images/icon/icon256_png.png',
                        'assets/images/icon/icon128_png.png',
                        'assets/images/icon/icon48_png.png',
                        'assets/images/icon/icon32_png.png',
                        'assets/images/icon/icon16_png.png']},
                'include_patterns': [
                    '**/yyagl/licenses/*',
                    '**/licenses/*',
                    '**/*.bam',
                    '**/*.txo',
                    '**/*.json',
                    '**/track_tr.py',
                    '**/*.txt',
                    '**/*.ttf',
                    '**/*.vert',
                    '**/*.frag',
                    '**/*.ogg',
                    '**/*.wav',
                    '**/*.mo'],
                'platforms': platform_lst,
                'include_modules': {'*': ['encodings.hex_codec']}},
            'bdist_apps': {
                'installers': installers_dct
                }}
    )
