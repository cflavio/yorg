def sender_dec(fun):

    def inner(msg, args=[]):
        fun_args = ((msg, args)) if isinstance(msg, basestring) \
            else (msg.__class__.__name__, [msg] + args)
        fun(*fun_args)

    return inner
