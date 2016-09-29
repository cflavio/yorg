'''This module provides functionalities for creating pdfs of source.'''
from os import system, rename, remove
from shutil import move
from .build import path, ver_branch, pdf_path_str


def build_pdf(target, source, env):
    '''Pdf building.'''
    pdfname = env['NAME']
    filt_game = ['./racing/game/thirdparty/*', './racing/game/tests/*']
    conf = {
        'sources': [
            ('python', '.', '*.py', ['./racing/*'])],
        'sources_racing': [
            ('python', './racing', '*.py', ['./racing/game/*'])],
        'sources_game': [
            ('python', './racing/game', '*.py', filt_game),
            ('lua', './racing/game', 'config.lua', filt_game),
            ('python', './racing/game', '*.pdef', filt_game),
            ('', './racing/game', '*.rst', filt_game),
            ('html', './racing/game', '*.html', filt_game),
            ('javascript', './racing/game', '*.js', filt_game),
            ('', './racing/game', '*.css_t', filt_game),
            ('', './racing/game', '*.conf', filt_game)
            ]
    }
    cmd_tmpl = "enscript --font=Courier11 --continuous-page-numbers " + \
        "{lang} -o - `find {root} -name '{wildcard}' " + \
        "{filter}` | ps2pdf - {name}.pdf ; " + \
        "pdfnup --nup 2x1 -o {name}.pdf {name}.pdf"
    for name, options in conf.items():
        for i, opt_lang in enumerate(options):
            filt = ''
            for fil in opt_lang[3]:
                filt += "-not -path '%s' " % fil
            lang = ('--pretty-print=' + opt_lang[0]) if opt_lang[0] else ''
            cmd = cmd_tmpl.format(lang=lang, root=opt_lang[1],
                                  wildcard=opt_lang[2], filter=filt, name=name)
            if i:
                rename(name + '.pdf', name + '_append.pdf')
                system(cmd)
                cmd = 'gs -q -sPAPERSIZE=a4 -dNOPAUSE -dBATCH ' + \
                    '-sDEVICE=pdfwrite -sOutputFile={name}-joined.pdf ' + \
                    '{name}_append.pdf {name}.pdf'
                system(cmd.format(name=name))
                remove(name + '.pdf')
                remove(name + '_append.pdf')
                move(name + '-joined.pdf', name + '.pdf')
            else:
                system(cmd)
    pdfs = ''
    for name in conf:
        pdfs += name + '.pdf '
    cmd = 'tar -czf {out_name} ' + pdfs + ' && rm ' + pdfs
    pdf_path = pdf_path_str.format(path=path, name=pdfname, version=ver_branch)
    cmd = cmd.format(out_name=pdf_path)
    system(cmd)
