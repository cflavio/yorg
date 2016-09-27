'''The sender decorator.'''


def sender_dec(fun):
    '''The decorator.'''

    def inner(msg, args=[]):
        '''The inner function.'''
        fun_args = ((msg, args)) if isinstance(msg, basestring) \
            else (msg.__class__.__name__, [msg] + args)
        fun(*fun_args)

    return inner
