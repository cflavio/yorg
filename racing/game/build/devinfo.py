from os import system
from .build import path, ver_branch, exec_cmd, devinfo_path_str


def __clean_pylint(pylint_out):
    clean_out = ''
    skipping = False
    err_str = 'No config file found, using default configuration'
    lines = [line for line in pylint_out.split('\n') if line != err_str]
    for line in lines:
        if line == 'Traceback (most recent call last):':
            skipping = True
        elif line == 'RuntimeError: maximum recursion depth exceeded ' + \
                     'while calling a Python object':
            skipping = False
        elif not skipping:
            clean_out += line + '\n'
    return clean_out


def __process(src, cond, outfile):
    if cond(src):
        return
    outfile.write('    '+str(src)+'\n')
    out_pylint = __clean_pylint((exec_cmd('pylint -r n -d C0111 '+str(src))))
    out_pyflakes = exec_cmd('pyflakes '+str(src))
    out_pep8 = exec_cmd('pep8 ' + str(src))
    outs = [out.strip() for out in [out_pylint, out_pyflakes, out_pep8]]
    map(lambda out: outfile.write(out+'\n'), [out for out in outs if out])
    outfile.write('\n')


def build_devinfo(target, source, env):
    name = env['NAME']
    dev_conf = env['DEV_CONF']
    for fname, cond in dev_conf.items():
        for src in source:
            with open(('%s%s.txt') % (path, fname), 'a') as outfile:
                __process(src, cond, outfile)
    names = ''.join([fname + '.txt ' for fname in dev_conf])
    rmnames = ''.join(['{path}' + fname + '.txt ' for fname in dev_conf])
    build_command_str = \
        'tar -czf {out_name} -C {path} ' + names + ' && rm ' + rmnames
    fpath = devinfo_path_str.format(path=path, name=name, version=ver_branch)
    system(build_command_str.format(path=path, out_name=fpath))
