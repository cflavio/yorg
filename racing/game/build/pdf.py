'''This module provides functionalities for creating pdfs of source.'''
from os import system
from .build import path, ver_branch, pdf_path_str


def build_pdf(target, source, env):
    '''Pdf building.'''
    name = env['NAME']
    cmd_tmpl = "enscript --font=Courier11 --continuous-page-numbers " + \
        "--pretty-print=python -o - `{find}` | " + \
        "ps2pdf - {name}.pdf ; pdfnup --nup 2x1 -o {name}.pdf {name}.pdf"
    find_yorg = "find . -name '*.py' -not -path './racing/*'"
    find_racing = "find ./racing -name '*.py' -not -path './racing/game/*'"
    find_game = "find ./racing/game -name '*.py' " + \
        "-not -path './racing/game/thirdparty/*' " + \
        "-not -path './racing/game/tests/*'"
    finds = [find_yorg, find_racing, find_game]
    names = ['sources', 'sources_racing', 'sources_game']
    for find, fname in zip(finds, names):
        cmd = cmd_tmpl.format(find=find, name=fname)
        system(cmd)
    cmd = 'tar -czf {out_name} sources.pdf sources_racing.pdf ' + \
        'sources_game.pdf && rm sources.pdf sources_racing.pdf ' + \
        'sources_game.pdf'
    pdf_path = pdf_path_str.format(path=path, name=name, version=ver_branch)
    cmd = cmd.format(out_name=pdf_path)
    system(cmd)
