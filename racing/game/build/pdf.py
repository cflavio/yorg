'''This module provides functionalities for creating pdfs of source.'''
from os import system
from .build import path, ver_branch, pdf_path_str


def build_pdf(target, source, env):
    '''Pdf building.'''
    name = env['NAME']
    cmd = "enscript --font=Courier11 --continuous-page-numbers " + \
        "--pretty-print=python -o - `find . -name '*.py' -not -path " + \
        "'./racing/*'` | " + \
        "ps2pdf - sources.pdf ; pdfnup --nup 2x1 -o sources.pdf sources.pdf"
    system(cmd)
    cmd = "enscript --font=Courier11 --continuous-page-numbers " + \
        "--pretty-print=python -o - `find ./racing -name '*.py' " + \
        "-not -path './racing/game/*'` | " + \
        "ps2pdf - sources_racing.pdf ; pdfnup --nup 2x1 " + \
        "-o sources_racing.pdf sources_racing.pdf"
    system(cmd)
    cmd = "enscript --font=Courier11 --continuous-page-numbers " + \
        "--pretty-print=python -o - `find ./racing/game -name '*.py' " + \
        "-not -path './racing/game/thirdparty/*' " + \
        "-not -path './racing/game/tests/*'` | " + \
        "ps2pdf - sources_game.pdf ; pdfnup --nup 2x1 -o sources_game.pdf " + \
        "sources_game.pdf"
    system(cmd)
    cmd = 'tar -czf {out_name} sources.pdf sources_racing.pdf ' + \
        'sources_game.pdf && rm sources.pdf sources_racing.pdf ' + \
        'sources_game.pdf'
    cmd = cmd.format(
        out_name=pdf_path_str.format(path=path, name=name, version=ver_branch))
    system(cmd)
