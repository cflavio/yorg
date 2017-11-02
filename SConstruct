from collections import namedtuple
from yyagl.build.build import extensions, files, img_tgt_names, \
    set_path, p3d_fpath, win_fpath, osx_fpath, linux_fpath, \
    src_fpath, devinfo_fpath, docs_fpath, win_noint_fpath,\
    osx_noint_fpath, linux_noint_fpath, pdf_fpath, test_fpath, \
    tracks_tgt_fnames
from yyagl.build.p3d import bld_p3d
from yyagl.build.windows import bld_windows
from yyagl.build.osx import bld_osx
from yyagl.build.linux import bld_linux
from yyagl.build.src import bld_src
from yyagl.build.devinfo import bld_devinfo
from yyagl.build.test import bld_ut
from yyagl.build.docs import bld_docs
from yyagl.build.strings import bld_strings, bld_tmpl_merge
from yyagl.build.imgs import bld_images
from yyagl.build.pdf import bld_pdfs
from yyagl.build.tracks import bld_models


argument_info = [  # (argname, default value)
    ('path', 'built'), ('lang', 0), ('p3d', 0), ('source', 0), ('devinfo', 0),
    ('windows', 0), ('osx', 0), ('linux_32', 0), ('linux_64', 0), ('docs', 0),
    ('images', 0), ('tracks', 0), ('deployng', 0), ('nointernet', 0),
    ('pdf', 0), ('tests', 0), ('cores', 0)]
args = {arg: ARGUMENTS.get(arg, default) for (arg, default) in argument_info}
full_bld = any(args[arg] for arg in ['windows', 'osx', 'linux_32', 'linux_64'])
args['images'] = args['images'] or args['deployng'] or args['p3d'] \
    or full_bld or args['source']
args['lang'] = args['lang'] or args['deployng'] or args['p3d'] or full_bld or \
    args['source']
args['tracks'] = args['tracks'] or args['deployng'] or args['p3d'] or \
    full_bld or args['source']
args['p3d'] = args['p3d'] or (full_bld and not args['deployng'])
path = set_path(args['path'])
app_name = 'yorg'
lang_path = 'assets/locale/'

pargs = {'dst_dir': path, 'appname': app_name}
p3d_path = p3d_fpath.format(**pargs)
win_path = win_fpath.format(**pargs)
osx_path = osx_fpath.format(**pargs)
linux_path_32 = linux_fpath.format(platform='i386', **pargs)
linux_path_64 = linux_fpath.format(platform='amd64', **pargs)
win_path_noint = win_noint_fpath.format(**pargs)
osx_path_noint = osx_noint_fpath.format(**pargs)
linux_path_32_noint = linux_noint_fpath.format(platform='i386', **pargs)
linux_path_64_noint = linux_noint_fpath.format(platform='amd64', **pargs)
src_path = src_fpath.format(**pargs)
devinfo_path = devinfo_fpath.format(**pargs)
tests_path = test_fpath.format(**pargs)
docs_path = docs_fpath.format(**pargs)
pdf_path = pdf_fpath.format(**pargs)

bld_p3d = Builder(action=bld_p3d)
bld_windows = Builder(action=bld_windows)
bld_osx = Builder(action=bld_osx)
bld_linux = Builder(action=bld_linux)
bld_src = Builder(action=bld_src)
bld_devinfo = Builder(action=bld_devinfo)
bld_tests = Builder(action=bld_ut)
bld_docs = Builder(action=bld_docs)
bld_pdfs = Builder(action=bld_pdfs)
bld_images = Builder(action=bld_images)
bld_models = Builder(action=bld_models)
bld_str = Builder(action=bld_strings, suffix='.mo', src_suffix='.po')
bld_str_tmpl = Builder(action=bld_tmpl_merge, suffix='.pot',
                       src_suffix='.py')

env = Environment(BUILDERS={
    'p3d': bld_p3d, 'windows': bld_windows, 'osx': bld_osx, 'linux': bld_linux,
    'source': bld_src, 'devinfo': bld_devinfo, 'tests': bld_tests,
    'docs': bld_docs, 'images': bld_images, 'str': bld_str,
    'str_tmpl': bld_str_tmpl, 'pdf': bld_pdfs, 'tracks': bld_models})
env['P3D_PATH'] = p3d_path
env['APPNAME'] = app_name
env['LNG'] = lang_path
env['NOINTERNET'] = args['nointernet']
env['DEPLOYNG'] = args['deployng']
env['ICO_FPATH'] = 'assets/images/icon/icon%s_png.png'
env['LANGUAGES'] = ['it_IT', 'de_DE']
env['MODELS_DIR_PATH'] = 'assets/models'
env['TRACKS_DIR_PATH'] = 'assets/models/tracks'
env['CORES'] = int(args['cores'])
PDFInfo = namedtuple('PDFInfo', 'lng root fil excl')
filt_game = ['./yyagl/racing/*', './yyagl/thirdparty/*']
yorg_fil_dirs = ['yyagl', 'menu', 'yorg', 'licenses', 'assets', 'venv',
                 'build', 'built']
yorg_fil = ['./%s/*' % dname for dname in yorg_fil_dirs]
yorg_lst = [
    PDFInfo('python', './yorg', '*.py', []),
    PDFInfo('python', '.', '*.py SConstruct *.md *.txt', yorg_fil)]
racing_fil = ['./yyagl/racing/game/*', './yyagl/racing/car/*',
              './yyagl/racing/race/*', './yyagl/racing/track/*']
racing_lst = [PDFInfo('python', './yyagl/racing', '*.py', racing_fil)]
yyagl_fil = ['./yyagl/build/*', './yyagl/engine/*', './yyagl/tests/*']
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
    'yorg': yorg_lst,
    'racing': racing_lst,
    'racing_car': [PDFInfo('python', './yyagl/racing/car', '*.py', [])],
    'racing_race': [PDFInfo('python', './yyagl/racing/race', '*.py', [])],
    'racing_track': [PDFInfo('python', './yyagl/racing/track', '*.py', [])],
    'yyagl': yyagl_lst,
    'build': build_lst,
    'engine': [PDFInfo('python', './yyagl/engine', '*.py', ['./yyagl/engine/gui/*', './yyagl/engine/network/*'])],
    'engine_gui': [PDFInfo('python', './yyagl/engine/gui', '*.py', [])],
    'engine_network': [PDFInfo('python', './yyagl/engine/network', '*.py', [])],
    'tests': [PDFInfo('python', './yyagl/tests', '*.py', [])]}
env['PDF_CONF'] = pdf_conf

cond_racing = lambda s: not str(s).startswith('yyagl/racing/')
def cond_yyagl(src):
    not_yyagl = not str(src).startswith('yyagl/')
    thirdparty = str(src).startswith('yyagl/thirdparty/')
    venv = str(src).startswith('venv/')
    racing = str(src).startswith('yyagl/racing/')
    return not_yyagl or thirdparty or venv or racing or \
        str(src).startswith('yyagl/tests')
dev_conf = {'devinfo': lambda s: str(s).startswith('yyagl/'),
            'devinfo_racing': cond_racing, 'devinfo_yyagl': cond_yyagl}
env['DEV_CONF'] = dev_conf

VariantDir(path, '.')

img_files = img_tgt_names(files(['png']))
lang_src = [lang_path + 'it_IT/LC_MESSAGES/%s.mo' % app_name,
            lang_path + 'de_DE/LC_MESSAGES/%s.mo' % app_name]
general_src = files(extensions, ['venv', 'thirdparty']) + img_files + \
    lang_src + tracks_tgt_fnames()
no_int = args['nointernet']
if args['images']:
    env.images(img_files, files(['jpg', 'png'], ['models'], ['_png.png']))
if args['tracks']:
    env.tracks(tracks_tgt_fnames(), files(['egg']))
if args['p3d']:
    env.p3d([p3d_path], general_src)
if args['source']:
    env.source([src_path], general_src)
if args['devinfo']:
    env.devinfo([devinfo_path], files(['py'], ['venv', 'thirdparty']))
if args['tests']:
    env.tests([tests_path], files(['py'], ['venv', 'thirdparty']))
if args['windows']:
    out_wpath = win_path_noint if args['nointernet'] else win_path
    env.windows([out_wpath], general_src if args['deployng'] else [p3d_path])
if args['osx']:
    out_opath = osx_path_noint if args['nointernet'] else osx_path
    env.osx([out_opath], general_src if args['deployng'] else [p3d_path])
if args['linux_32']:
    out_lpath32 = linux_path_32_noint if no_int else linux_path_32
    env.linux([out_lpath32], general_src if args['deployng'] else [p3d_path],
              PLATFORM='i386')
if args['linux_64']:
    out_lpath64 = linux_path_64_noint if no_int else linux_path_64
    env.linux([out_lpath64], general_src if args['deployng'] else [p3d_path],
              PLATFORM='amd64')
if args['docs']:
    env.docs([docs_path], files(['py'], ['venv', 'thirdparty']))
if args['pdf']:
    env.pdf([pdf_path], files(['py'], ['venv', 'thirdparty']))

def process_lang(lang_code):
    lang_name = lang_path + lang_code + '/LC_MESSAGES/%s.po' % app_name
    tmpl = env.str_tmpl(lang_name, files(['py'], ['venv', 'thirdparty']))
    env.NoClean(tmpl)
    lang_mo = lang_path + lang_code + '/LC_MESSAGES/%s.mo' % app_name
    lang_po = lang_path + lang_code + '/LC_MESSAGES/%s.po' % app_name
    env.str(lang_mo, lang_po)

if args['lang']:
    map(process_lang, ['it_IT', 'de_DE'])
