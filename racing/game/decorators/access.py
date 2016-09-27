'''The access decorator.'''
from inspect import getmembers, ismethod
from itertools import product


def __pvt_name(cls_str, attr):
    '''The private name.'''
    return '_'+cls_str+'__'+attr


def _get_meth(cls, attr):
    '''The getter.'''

    def __get_meth(self):
        '''The getter implementation.'''
        get_attr = lambda cls_str: \
            self.__getattribute__(__pvt_name(cls_str, attr))
        try:
            return get_attr(cls.__name__)
        except AttributeError:
            return get_attr(self.__class__.__name__)

    return __get_meth


def auto_properties(cls):
    '''The decorator.'''
    methods = getmembers(cls, predicate=ismethod)
    meth_names = map(lambda memb: memb[0], methods)

    getter_names = filter(
        lambda meth_name: meth_name.startswith('get_')
        and 'set_'+meth_name[4:] not in meth_names,
        meth_names)
    getters = filter(lambda meth: meth[0] in getter_names, methods)
    map(lambda getter: setattr(cls, getter[0][4:], property(getter[1])),
        getters)

    setter_names = filter(
        lambda meth_name: meth_name.startswith('set_')
        and 'get_'+meth_name[4:] not in meth_names,
        meth_names)
    setters = filter(lambda meth: meth[0] in setter_names, methods)
    map(lambda setter: setattr(cls, setter[0][4:],
        property(_get_meth(cls, setter[0][4:]), setter[1])),
        setters)

    set_get_names = filter(
        lambda meth_name: meth_name.startswith('set_')
        and 'get_'+meth_name[4:] in meth_names,
        meth_names)
    set_getters = filter(
        lambda meth_pairs: meth_pairs[0][0] in set_get_names
        and meth_pairs[1][0] == 'get_' + meth_pairs[0][0][4:],
        product(methods, methods))
    map(lambda set_getter: setattr(cls, set_getter[0][0][4:],
                                   property(set_getter[1][1],
                                            set_getter[0][1])),
        set_getters)

    return cls
