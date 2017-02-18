from yyagl.build.build import extensions, get_files, image_extensions, \
    set_path, p3d_path_str, win_path_str, osx_path_str, linux_path_str, \
    src_path_str, devinfo_path_str, docs_path_str, win_path_noint_str,\
    osx_path_noint_str, linux_path_noint_str, pdf_path_str, test_path_str
from yyagl.build.p3d import build_p3d
from yyagl.build.windows import build_windows
from yyagl.build.osx import build_osx
from yyagl.build.linux import build_linux
from yyagl.build.src import build_src
from yyagl.build.devinfo import build_devinfo
from yyagl.build.test import build_ut
from yyagl.build.docs import build_docs
from yyagl.build.strings import build_strings, build_string_template
from yyagl.build.imgs import build_images
from yyagl.build.pdf import build_pdf


argument_info = [
    ('path', 'built'), ('lang', 0), ('p3d', 0), ('source', 0), ('devinfo', 0),
    ('windows', 0), ('osx', 0), ('linux_32', 0), ('linux_64', 0), ('docs', 0),
    ('images', 0), ('nointernet', 0), ('pdf', 0), ('tests', 0)]
arguments = dict((arg, ARGUMENTS.get(arg, default))
                  for arg, default in argument_info)
if any(arguments[arg] for arg in ['windows', 'osx', 'linux_32', 'linux_64']):
    arguments['p3d'] = 1
if arguments['p3d'] or arguments['source']:
    arguments['images'] = 1
    arguments['lang'] = 1
path = set_path(arguments['path'])
app_name = 'yorg'
lang_path = 'assets/locale/'

args = {'path': path, 'name': app_name}
p3d_path = p3d_path_str.format(**args)
win_path = win_path_str.format(**args)
osx_path = osx_path_str.format(**args)
linux_path_32 = linux_path_str.format(platform='i386', **args)
linux_path_64 = linux_path_str.format(platform='amd64', **args)
win_path_noint = win_path_noint_str.format(**args)
osx_path_noint = osx_path_noint_str.format(**args)
linux_path_32_noint = linux_path_noint_str.format(platform='i386', **args)
linux_path_64_noint = linux_path_noint_str.format(platform='amd64', **args)
src_path = src_path_str.format(**args)
devinfo_path = devinfo_path_str.format(**args)
tests_path = test_path_str.format(**args)
docs_path = docs_path_str.format(**args)
pdf_path = pdf_path_str.format(**args)

bld_p3d = Builder(action=build_p3d)
bld_windows = Builder(action=build_windows)
bld_osx = Builder(action=build_osx)
bld_linux = Builder(action=build_linux)
bld_src = Builder(action=build_src)
bld_devinfo = Builder(action=build_devinfo)
bld_tests = Builder(action=build_ut)
bld_docs = Builder(action=build_docs)
bld_pdf = Builder(action=build_pdf)
bld_images = Builder(action=build_images)
bld_str = Builder(action=build_strings, suffix='.mo', src_suffix='.po')
bld_str_tmpl = Builder(action=build_string_template, suffix='.pot',
                       src_suffix='.py')

env = Environment(BUILDERS={
    'p3d': bld_p3d, 'windows': bld_windows, 'osx': bld_osx, 'linux': bld_linux,
    'source': bld_src, 'devinfo': bld_devinfo, 'tests': bld_tests,
    'docs': bld_docs, 'images': bld_images, 'str': bld_str,
    'str_tmpl': bld_str_tmpl, 'pdf': bld_pdf})
env['P3D_PATH'] = p3d_path
env['NAME'] = app_name
env['LANG'] = lang_path
env['NOINTERNET'] = arguments['nointernet']
env['ICO_FILE'] = 'assets/images/icon/icon%s_png.png'
env['LANGUAGES'] = ['it_IT']
env['SUPERMIRROR'] = ''
filt_game = ['./yyagl/racing/*', './yyagl/thirdparty/*']
pdf_conf = {
    'yorg_menu': [
        ('python', './menu', '*.py', [])],
    'yorg_yorg': [
        ('python', './yorg', '*.py', [])],
    'yorg': [
        ('python', '.', '*.py SConstruct *.md *.txt', ['./yyagl/*', './menu/*', './yorg/*', './licenses/*', './assets/*'])],
    'racing': [
        ('python', './yyagl/racing', '*.py', ['./yyagl/racing/game/*', './yyagl/racing/car/*', './yyagl/racing/race/*', './yyagl/racing/ranking/*', './yyagl/racing/season/*', './yyagl/racing/track/*', './yyagl/racing/tuning/*', './yyagl/racing/weapon/*'])],
    'racing_car': [
        ('python', './yyagl/racing/car', '*.py', [])],
    'racing_race': [
        ('python', './yyagl/racing/race', '*.py', [])],
    'racing_ranking': [
        ('python', './yyagl/racing/ranking', '*.py', [])],
    'racing_season': [
        ('python', './yyagl/racing/season', '*.py', [])],
    'racing_track': [
        ('python', './yyagl/racing/track', '*.py', [])],
    'racing_tuning': [
        ('python', './yyagl/racing/tuning', '*.py', [])],
    'racing_weapon': [
        ('python', './yyagl/racing/weapon', '*.py', [])],
    'yyagl': [
        ('python', './yyagl', '*.py *.pdef', filt_game + ['./yyagl/build/*', './yyagl/engine/*', './yyagl/tests/*']),
        ('c', './yyagl', '*.vert *.frag', filt_game + ['./yyagl/build/*', './yyagl/engine/*', './yyagl/tests/*']),
        ],
    'build': [
        ('python', './yyagl/build', '*.py *.pdef', filt_game),
        ('lua', './yyagl/build', 'config.lua', filt_game),
        ('', './yyagl/build', '*.rst *.css_t *.conf', filt_game),
        ('html', './yyagl/build', '*.html', filt_game),
        ('javascript', './yyagl/build', '*.js', filt_game)],
    'engine': [
        ('python', './yyagl/engine', '*.py', filt_game)],
    'tests': [
        ('python', './yyagl/tests', '*.py', [])]}
env['PDF_CONF'] = pdf_conf

def cond_racing(s):
    return not str(s).startswith('yyagl/racing/')# or str(s).startswith('racing/game/')
def cond_yyagl(src):
    not_yyagl = not str(src).startswith('yyagl/')
    thirdparty = str(src).startswith('yyagl/thirdparty/')
    racing = str(src).startswith('yyagl/racing/')
    return not_yyagl or thirdparty or racing or str(src).startswith('yyagl/tests')
dev_conf = {'devinfo': lambda s: str(s).startswith('yyagl/'),
            'devinfo_racing': cond_racing, 'devinfo_yyagl': cond_yyagl}
env['DEV_CONF'] = dev_conf

VariantDir(path, '.')

img_files = image_extensions(get_files(['psd']))
if arguments['images']:
    env.images(img_files, get_files(['psd']))
if arguments['p3d']:
    src_p3d = get_files(extensions) + img_files + \
        [lang_path+'it_IT/LC_MESSAGES/%s.mo' % app_name]
    env.p3d([p3d_path], src_p3d)
if arguments['source']:
    src_src = get_files(extensions) + img_files + \
        [lang_path+'it_IT/LC_MESSAGES/%s.mo' % app_name]
    env.source([src_path], src_src)
if arguments['devinfo']:
    env.devinfo([devinfo_path], get_files(['py']))
if arguments['tests']:
    env.tests([tests_path], get_files(['py']))
if arguments['windows']:
    out_path = win_path_noint if arguments['nointernet'] else win_path
    env.windows([out_path], [p3d_path])
if arguments['osx']:
    out_path = osx_path_noint if arguments['nointernet'] else osx_path
    env.osx([out_path], [p3d_path])
if arguments['linux_32']:
    out_path = linux_path_32_noint if arguments['nointernet'] \
        else linux_path_32
    env.linux([out_path], [p3d_path], PLATFORM='i386')
if arguments['linux_64']:
    out_path = linux_path_64_noint if arguments['nointernet'] \
        else linux_path_64
    env.linux([out_path], [p3d_path], PLATFORM='amd64')
if arguments['docs']:
    env.docs([docs_path], get_files(['py']))
if arguments['pdf']:
    env.pdf([pdf_path], get_files(['py']))

def process_lang(lang_code):
    tmpl = env.str_tmpl(
        lang_path+lang_code+'/LC_MESSAGES/%s.po' % app_name,
        get_files(['py']))
    env.Precious(tmpl)
    env.str(lang_path+lang_code+'/LC_MESSAGES/%s.mo' % app_name,
            lang_path+lang_code+'/LC_MESSAGES/%s.po' % app_name)

if arguments['lang']:
    for lang_code in ['it_IT']:
        process_lang(lang_code)
