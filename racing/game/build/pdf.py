'''This module provides functionalities for creating pdfs of source.'''
from os import system, rename, remove
from itertools import product
from shutil import move
from .build import path, ver_branch, pdf_path_str


def __process(opt_lang, cmd_tmpl, name, i):
    '''Processes a file.'''
    filt = ''
    for fil in opt_lang[3]:
        filt += "-not -path '%s' " % fil
    lang = ('--pretty-print=' + opt_lang[0]) if opt_lang[0] else ''
    wcard = '-o '.join(["-name '%s' " % wld for wld in opt_lang[2].split()])
    wcard = '\\( %s\\)' % wcard
    cmd = cmd_tmpl.format(lang=lang, root=opt_lang[1],
                          wildcard=wcard, filter=filt, name=name)
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


def build_pdf(target, source, env):
    '''Pdf building.'''
    pdfname = env['NAME']
    conf = env['PDF_CONF']
    cmd_tmpl = "enscript --font=Courier10 --continuous-page-numbers " + \
        "--line-numbers {lang} -o - `find {root} {wildcard} " + \
        "{filter}` | ps2pdf - {name}.pdf"
    cmd_cont_tmpl = "tail -n +1 `find {root} {wildcard} {filter}` " + \
        "| sed 's/==> /# ==> /' > temp.txt ; enscript --font=Courier10 " + \
        "--continuous-page-numbers --no-header {lang} -o - " + \
        "temp.txt | ps2pdf - {name}.pdf ; rm temp.txt"

    for name, options in conf.items():
        for (i, opt_lang), suff in product(enumerate(options), ['', '_cont']):
            cmd = cmd_cont_tmpl if suff else cmd_tmpl
            __process(opt_lang, cmd, name + suff, i)
        cmd_pdf_tmpl = 'pdfnup --nup 2x1 -o {name}.pdf {name}.pdf'
        for name_s in [name + '', name + '_cont']:
            system(cmd_pdf_tmpl.format(name=name_s))
    pdfs = ''.join([name + '.pdf ' for name in conf])
    pdfs += ''.join([name + '_cont.pdf ' for name in conf])
    cmd = 'tar -czf {out_name} ' + pdfs + ' && rm ' + pdfs
    pdf_path = pdf_path_str.format(path=path, name=pdfname, version=ver_branch)
    cmd = cmd.format(out_name=pdf_path)
    system(cmd)
