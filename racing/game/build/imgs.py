'''This module provides functionalities for building images.'''
from os import system, remove
from .build import exec_cmd


def __get_img_fmt(_file):
    '''Returns image info.'''
    cmd = 'identify -verbose "%s" | grep alpha' % _file
    alpha = exec_cmd(cmd).strip()
    geometry = exec_cmd('identify -verbose "%s" | grep Geometry' % _file)
    split_dim = lambda geom: geom.split()[1].split('+')[0].split('x')
    size = [int(dim) for dim in split_dim(geometry)]
    return alpha, size


def __build_img(_file):
    '''Builds an image.'''
    png = _file[:-3]+'png'
    alpha, size = __get_img_fmt(_file)
    sizes = [2**i for i in range(0, 12)]
    low_pow = lambda x: max([y for y in sizes if y <= x])
    width, height = map(low_pow, size)
    system('convert "%s"[0] -resize %dx%d! "%s"' % (_file, width, height, png))
    if png.endswith('_png.png'):
        return
    cmd = 'nvcompress -bc3 '+('-alpha' if alpha else '') + \
        ' -nomips "' + png + '" "' + _file[:-3] + 'dds"'
    system(cmd)
    remove(png)


def build_images(target, source, env):
    '''Builds the images.'''
    map(lambda _file: __build_img(_file), [str(src) for src in source])
