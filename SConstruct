from collections import namedtuple
from yyagl.build.build import extensions, files, img_tgt_names, \
    set_path, win_fpath, osx_fpath, linux_fpath, flatpak_fpath, src_fpath, \
    devinfo_fpath, docs_fpath, pdf_fpath, test_fpath, tracks_tgt_fnames, \
    appimage_fpath
from yyagl.build.windows import bld_windows
from yyagl.build.osx import bld_osx
from yyagl.build.linux import bld_linux
from yyagl.build.flatpak import bld_flatpak
from yyagl.build.appimage import bld_appimage
from yyagl.build.src import bld_src
from yyagl.build.devinfo import bld_devinfo
from yyagl.build.docs import bld_docs
from yyagl.build.strings import bld_mo, bld_pot, bld_merge
from yyagl.build.imgs import bld_images
from yyagl.build.pdf import bld_pdfs
from yyagl.build.tracks import bld_models
from yyagl.build.uml import bld_uml


SCONS_ENABLE_VIRTUALENV=1
argument_info = [  # (argname, default value)
    ('path', 'built'), ('lang', 0), ('p3d', 0), ('source', 0), ('devinfo', 0),
    ('windows', 0), ('osx', 0), ('linux', 0), ('docs', 0), ('images', 0),
    ('tracks', 0), ('pdf', 0), ('cores', 0), ('uml', 0),
    ('flatpak', 0), ('flatpak_dst', '.'), ('appimage', 0)]
args = {arg: ARGUMENTS.get(arg, default) for (arg, default) in argument_info}
full_bld = any(args[arg] for arg in ['windows', 'osx', 'linux', 'flatpak', 'appimage'])
args['images'] = args['images'] or full_bld or args['source']
args['lang'] = args['lang'] or full_bld or args['source']
args['tracks'] = args['tracks'] or full_bld or args['source']
path = set_path(args['path'])
app_name = 'yorg'
lang_path = 'assets/locale/'

pargs = {'dst_dir': path, 'appname': app_name}
win_path = win_fpath.format(**pargs)
osx_path = osx_fpath.format(**pargs)
linux_path = linux_fpath.format(**pargs)
flatpak_path = flatpak_fpath.format(**pargs)
appimage_path = appimage_fpath.format(**pargs)
src_path = src_fpath.format(**pargs)
devinfo_path = devinfo_fpath.format(**pargs)
docs_path = docs_fpath.format(**pargs)
pdf_path = pdf_fpath.format(**pargs)

bld_windows = Builder(action=bld_windows)
bld_osx = Builder(action=bld_osx)
bld_linux = Builder(action=bld_linux)
bld_flatpak = Builder(action=bld_flatpak)
bld_appimage = Builder(action=bld_appimage)
bld_src = Builder(action=bld_src)
bld_devinfo = Builder(action=bld_devinfo)
bld_docs = Builder(action=bld_docs)
bld_pdfs = Builder(action=bld_pdfs)
bld_images = Builder(action=bld_images)
bld_models = Builder(action=bld_models)
bld_mo = Builder(action=bld_mo, suffix='.mo', src_suffix='.po')
bld_pot = Builder(action=bld_pot, suffix='.pot', src_suffix='.py')
bld_merge = Builder(action=bld_merge, suffix='.po', src_suffix='.pot')
bld_uml = Builder(action=bld_uml)

env = Environment(BUILDERS={
    'windows': bld_windows, 'osx': bld_osx, 'linux': bld_linux,
    'source': bld_src, 'devinfo': bld_devinfo,
    'docs': bld_docs, 'images': bld_images, 'mo': bld_mo, 'pot': bld_pot,
    'merge': bld_merge, 'pdf': bld_pdfs, 'tracks': bld_models,
    'uml': bld_uml, 'flatpak': bld_flatpak, 'appimage': bld_appimage})
env['APPNAME'] = app_name
env['LNG'] = lang_path
env['ICO_FPATH'] = 'assets/images/icon/icon%s_png.png'
env['LANGUAGES'] = ['it_IT', 'de_DE', 'gd', 'es_ES', 'gl_ES', 'fr_FR']
env['MODELS_DIR_PATH'] = 'assets/models'
env['CARS_DIR_PATH'] = 'assets/cars'
env['TRACKS_DIR_PATH'] = 'assets/tracks'
env['CORES'] = int(args['cores'])
env['FLATPAK_DST'] = args['flatpak_dst']
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
env['PDF_CONF'] = pdf_conf

dev_conf = {'devinfo': lambda s: str(s).startswith('yyagl/') or str(s).startswith('yracing/')}
env['DEV_CONF'] = dev_conf

env['UML_FILTER'] = ['yyagl', 'yracing']

VariantDir(path, '.')

img_files = img_tgt_names(files(['jpg', 'png'], ['models'], ['_png.png']))
langs = ['de_DE', 'es_ES', 'fr_FR', 'gd', 'gl_ES', 'it_IT']
lang_src = [lang_path + '%s/LC_MESSAGES/%s.mo' % (lng, app_name) for lng in langs]
general_src = files(extensions, ['venv', 'thirdparty', 'built']) + img_files + \
    lang_src + tracks_tgt_fnames()
if args['images']:
    imgs = env.images(img_files, files(['jpg', 'png'], ['models'], ['_png.png']))
    env.Precious(imgs)
if args['tracks']:
    tracks = env.tracks(tracks_tgt_fnames(), files(['egg']))
    env.Precious(tracks)
if args['source']:
    env.source([src_path], general_src)
if args['devinfo']:
    env.devinfo([devinfo_path], files(['py'], ['venv', 'thirdparty']))
if args['windows']:
    env.windows([win_path], general_src)
if args['osx']:
    env.osx([osx_path], general_src)
if args['linux']:
    env.linux([linux_path], general_src)
if args['flatpak']:
    env.flatpak([flatpak_path], general_src)
if args['appimage']:
    env.appimage([appimage_path], general_src)
if args['docs']:
    env.docs([docs_path], files(['py'], ['venv', 'thirdparty']))
if args['pdf']:
    env.pdf([pdf_path], files(['py'], ['venv', 'thirdparty']))
if args['uml']:
    env.uml(
        ['assets/uml/sequence_diagrams.pdf',
         'built/uml_classes.zip'],
        ['assets/uml/sequence_diagrams.txt'])

def process_lang(lang_code):
    lang_name = 'assets/po/%s.po' % lang_code
    tmpl = env.merge(lang_name, ['assets/po/yorg.pot'] + files(['py'], ['venv', 'thirdparty']))
    env.Precious(tmpl)
    env.NoClean(tmpl)
    lang_mo = lang_path + lang_code + '/LC_MESSAGES/%s.mo' % app_name
    lang_po = 'assets/po/%s.po' % lang_code
    env.mo(lang_mo, lang_po)

if args['lang']:
    env.pot('assets/po/yorg.pot', files(['py'], ['venv', 'thirdparty']))
    list(map(process_lang, ['it_IT', 'de_DE', 'gd', 'es_ES', 'gl_ES', 'fr_FR']))
