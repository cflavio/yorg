from os import path as os_path, remove, system, walk, chdir, getcwd, \
    makedirs, error
from os.path import expanduser, exists, basename
from shutil import move, rmtree, copytree, copy
from subprocess import Popen, PIPE
from build import ver, has_super_mirror, path, src_path_str, ver_branch, \
    exec_cmd, devinfo_path_str, pdf_path_str


def build_pdf(target, source, env):
    name = env['NAME']
    cmd = "enscript --font=Courier11 --continuous-page-numbers " + \
        "--pretty-print=python -o - `find . -name '*.py'` | " + \
        "ps2pdf - sources.pdf ; pdfnup --nup 2x1 -o sources.pdf sources.pdf"
    system(cmd)
    cmd = 'tar -czf {out_name} sources.pdf && rm sources.pdf'
    cmd = cmd.format(
        out_name=pdf_path_str.format(path=path, name=name, version=ver_branch))
    system(cmd)
