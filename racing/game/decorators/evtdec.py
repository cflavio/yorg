'''Decorator for events.'''
from direct.showbase.DirectObject import DirectObject
from functools import wraps
from inspect import getmro


def accept_dec(fun):
    '''Decorator of the accept function.'''
    def inner(msg, meth, args=[]):
        '''The inner function to be decorated.'''
        fun(msg, meth, args)
    return inner


def __evt_wrapper(self, fun, meths):
    '''Wrapping the event.'''

    @wraps(fun)
    def wrapper_evt(*args, **kargs):
        '''Actual event wrapper.'''
        for meth in meths:
            fun_name = meth.__name__
            states_index = fun_name.find('__')
            if states_index == -1:
                states, not_states = [], []
            else:
                states_str = fun_name[states_index+2:]
                if states_str.startswith('not_'):
                    states_str = states_str[4:]
                    states, not_states = [], states_str.split('__')
                else:
                    states, not_states = states_str.split('__'), []
            if self.__evt_dec_fsm:
                current_state = self.__evt_dec_fsm.getCurrentOrNextState()
            if not states and not not_states or \
                    states and current_state in states or \
                    not_states and current_state not in not_states:
                meth(*args, **kargs)

    return wrapper_evt


def __destroy_wrapper(self, fun):
    '''Removes the wrapper.'''

    @wraps(fun)
    def wrapper_destroy(*args, **kargs):
        '''The actual removal.'''
        self.ignoreAll()
        fun(*args, **kargs)

    return wrapper_destroy


def __evt_name(attr):
    '''Gets the event name.'''
    states_index = attr.find('__')
    return attr[4: states_index] if states_index != -1 else attr[4:]


def evt_dec(obj, fsm=None):
    '''The event decorator.'''
    obj.__evt_dec_fsm = fsm
    if DirectObject not in getmro(obj.__class__):
        obj.__class__.__bases__ += (DirectObject,)
    obj.accept = accept_dec(obj.accept)
    attrs = [getattr(obj, attr)
             for attr in dir(obj)
             if attr.startswith('evt_')]
    meths = [attr for attr in attrs if callable(attr)]
    for meth in meths:
        attr = meth.__name__
        msg_name = __evt_name(attr)
        evt_meths = [
            _meth
            for _meth in meths
            if _meth.__name__.startswith('evt_'+msg_name)
            and (not _meth.__name__.startswith('evt_'+msg_name+'up') or
                 not not _meth.__name__.startswith('evt_'+msg_name+'down'))
            and __evt_name(_meth.__name__) == msg_name]
        meth_wrapped = __evt_wrapper(obj, meth, evt_meths)
        setattr(obj, attr, meth_wrapped)
        if msg_name.endswith('up'):
            msg_name = msg_name[:-2]+'-up'
        obj.accept(msg_name, meth_wrapped)
    try:
        destroy_meth = getattr(obj, 'destroy')
    except AttributeError:
        destroy_meth = lambda self, *args, **kwargs: None
    setattr(obj, 'destroy', __destroy_wrapper(obj, destroy_meth))
