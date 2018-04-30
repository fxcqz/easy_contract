from functools import partial, update_wrapper
from inspect import getargspec


class contract(object):
    def __init__(self, fn):
        self.main = fn
        self.pre_funcs = []
        self.post_funcs = []
        self.fargs = getargspec(self.main).args
        self.instance = None

    def pre(self, fn):
        'Register a pre condition'
        self.pre_funcs.append(fn)

    def post(self, fn):
        'Register a post condition'
        self.post_funcs.append(fn)

    def create_old_args(self, *args, **kwargs):
        'Create a copy of the arguments to pass to the post condition'
        old = dict(zip(self.fargs, args))
        old.update(kwargs)
        return old

    def get_doc(self, fn):
        return fn.__doc__ or "No information"

    def make_error(self, fn, condition, error):
        return ('A {}-condition failed with the following message:\n{}\n'
                'With the error:\n{}'.format(
                    condition,
                    self.get_doc(fn),
                    error,
               ))

    def __get__(self, obj, type=None):
        self.instance = obj  # register the instance for later use
        return partial(self, obj)

    if __debug__:
        def __call__(self, *args, **kwargs):
            for func in self.pre_funcs:
                try:
                    func(*args, **kwargs)
                except AssertionError as e:
                    raise AssertionError(self.make_error(func, 'pre', e))

            result = self.main(*args, **kwargs)

            if self.post_funcs:
                kw_params = {'old': self.create_old_args(*args, **kwargs)}
                if self.instance:
                    params = (self.instance, result)
                else:
                    params = (result,)

                for func in self.post_funcs:
                    try:
                        func(*params, **kw_params)
                    except AssertionError as e:
                        raise AssertionError(self.make_error(func, 'post', e))

            return result
    else:
        # Assertions can't run, so don't even try
        def __call__(self, *args, **kwargs):
            return self.main(*args, **kwargs)
