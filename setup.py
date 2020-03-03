from os import system, getcwd
from collections import namedtuple
from setuptools import setup
from setuptools.command.develop import develop
from distutils.cmd import Command
from yyagl.build.build import files
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


class DevelopPyCmd(develop):

    def run(self):
        develop.run(self)
        system('scons lang=1 images=1 tracks=1')


class AbsCmd(Command):

    env = {'APPNAME': 'yorg'}
    user_options = [('cores', None, '#cores')]

    def initialize_options(self): self.cores = 0

    def finalize_options(self): AbsCmd.env['CORES'] = self.cores


class SourcePkgCmd(AbsCmd):

    def run(self): bld_src(None, None, AbsCmd.env)


class DevInfoCmd(AbsCmd):

    def run(self):
        dev_conf = {
            'devinfo': lambda s: str(s).startswith('./yyagl/') or \
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
        racing_lst = [PDFInfo('python', './yyagl/racing', '*.py', racing_fil)]
        yyagl_fil = ['./yyagl/build/*', './yyagl/engine/*', './yyagl/lib/*',
                     './yyagl/tests/*']
        yyagl_lst = [
            PDFInfo('python', './yyagl', '*.py *.pdef', filt_game + yyagl_fil),
            PDFInfo('c', './yyagl', '*.vert *.frag', filt_game + yyagl_fil)]
        binfo_lst = [
            ('python', '*.py *.pdef'), ('lua', 'config.lua'),
            ('', '*.rst *.css_t *.conf'), ('html', '*.html'), ('javascript', '*.js')]
        build_lst = [PDFInfo(binfo[0], './yyagl/build', binfo[1], filt_game)
                     for binfo in binfo_lst]
        pdf_conf = {
            'yorg_menu': [PDFInfo('python', './menu', '*.py', [])],
            'yorg': yorg_lst}
        AbsCmd.env['PDF_CONF'] = pdf_conf
        bld_pdfs(None, None, AbsCmd.env)


class ImagesCmd(AbsCmd):

    already_run = False

    def run(self):
        if ImagesCmd.already_run: return
        bld_images(
            None, files(['jpg', 'png'], ['tex'], ['_png.png']), AbsCmd.env)
        ImagesCmd.already_run = True


class UMLCmd(AbsCmd):

    def run(self):
        AbsCmd.env['UML_FILTER'] = ['yyagl', 'yracing']
        bld_uml(None, None, AbsCmd.env)


class ModelsCmd(AbsCmd):

    already_run = False

    def run(self):
        if ModelsCmd.already_run: return
        AbsCmd.env['MODELS_DIR_PATH'] = 'assets/models'
        AbsCmd.env['CARS_DIR_PATH'] = 'assets/cars'
        AbsCmd.env['TRACKS_DIR_PATH'] = 'assets/tracks'
        bld_models(None, None, AbsCmd.env)
        ModelsCmd.already_run = True


class LangCmd(AbsCmd):

    lang_path = 'assets/locale/'
    already_run = False

    def _process_lang(self, lang_code):
        lang_name = 'assets/po/%s.po' % lang_code
        bld_merge(lang_name, None, AbsCmd.env)
        lang_mo = self.lang_path + lang_code + '/LC_MESSAGES/%s.mo' % AbsCmd.env['APPNAME']
        bld_mo(lang_mo, None, AbsCmd.env)

    def run(self):
        if LangCmd.already_run: return
        AbsCmd.env['LNG'] = self.lang_path
        bld_pot(None, None, AbsCmd.env)
        list(map(self._process_lang, ['it_IT', 'de_DE', 'gd', 'es_ES', 'gl_ES', 'fr_FR']))
        LangCmd.already_run = True


class LinuxCmd(AbsCmd):

    def run(self):
        self.run_command('images')
        self.run_command('models')
        self.run_command('lang')
        AbsCmd.env['ICO_FPATH'] = 'assets/images/icon/icon%s_png.png'
        bld_linux(None, None, AbsCmd.env)


class WindowsCmd(AbsCmd):

    def run(self):
        self.run_command('images')
        self.run_command('models')
        self.run_command('lang')
        bld_windows(None, None, AbsCmd.env)


class AppImageCmd(AbsCmd):

    def run(self):
        self.run_command('images')
        self.run_command('models')
        self.run_command('lang')
        AbsCmd.env['ICO_FPATH'] = 'assets/images/icon/icon%s_png.png'
        bld_appimage(None, None, AbsCmd.env)


class FlatPakCmd(AbsCmd):

    def run(self):
        #self.run_command('images')
        #self.run_command('models')
        #self.run_command('lang')
        AbsCmd.env['ICO_FPATH'] = 'assets/images/icon/icon%s_png.png'
        AbsCmd.env['FLATPAK_DST'] = '.'
        bld_flatpak(None, None, AbsCmd.env)


if __name__ == '__main__':
    setup(
        name='Yorg',
        version=0.9,
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
            'linux': LinuxCmd,
            'windows': WindowsCmd,
            'appimage': AppImageCmd,
            'flatpak': FlatPakCmd},
        install_requires=[
            'SCons==2.5.0',
            # 'panda3d'  # it doesn't pull the dependency
            ])
