from functools import partial, update_wrapper
from inspect import getargspec


class contract(object):
    """
    Mark a function as a contract. Pre and post conditions can be subsequently
    defined for this contract.
    """
    def __init__(self, fn):
        self.main = fn
        self.pre_funcs = []
        self.post_funcs = []
        self.fargs = getargspec(self.main).args
        self.instance = None

    def requires(self, fn):
        'Register a pre condition'
        self.pre_funcs.append(fn)

    def ensures(self, fn):
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
                    raise AssertionError(self.make_error(func, 'requires', e))

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
                        raise AssertionError(self.make_error(func, 'ensures', e))

            return result
    else:
        # Assertions can't run, so don't even try
        def __call__(self, *args, **kwargs):
            return self.main(*args, **kwargs)


def _make_invariant(fn, *, predicate=None):
    """
    Wrapper for calling cls.__invariant__ before and after calls to fn.
    If a predicate is supplied, it must return true for __invariant__ to run
    before the call to fn.
    """
    def wrapper(self, *args, **kwargs):
        if predicate is None or (predicate and predicate(self, args)):
            # useful for a first time run of __setattr__ where the attribute
            # does not exist on the instance yet
            self.__invariant__()

        result = fn(self, *args, **kwargs)

        if predicate is None or (predicate and predicate(self, args)):
            self.__invariant__()

        return result
    return wrapper


def _wrap__init__(fn):
    def wrapper(self, *args, **kwargs):
        result = fn(self, *args, **kwargs)
        self._ezcontract_in__init__method = False
        return result
    return wrapper


def _super__init__(self, *args, **kwargs):
    return super(self.__class__, self).__init__(*args, **kwargs)


def _default__setattr__(self, name, value):
    super(self.__class__, self).__setattr__(name, value)


class Invariant(type):
    """
    Ensure an invariant method is run at opportune moments on a class.

    Supports __setattr__ and the iterator protocol (which requires the two
    functions __next__ and __iter__ to be defined).

    By default, __invariant__ will not be called during the __init__ function
    due to usability issues with __setattr__. To override this functionality,
    pass the 'check_init' metaclass kwarg to the class, e.g:

    >>> class Test(metaclass=Invariant, check_init=True): pass
    """
    @classmethod
    def _in__init__predicate(cls, self, args):
        # Use 'not' because it has to return true to run the predicate
        return not getattr(self, '_ezcontract_in__init__method', False)

    @classmethod
    def identity_predicate(cls, self, args):
        return True

    def __new__(cls, name, bases, attrs, *, check_init=False):
        if '__invariant__' not in attrs:
            raise Exception(
                f'Missing __invariant__ function for Invariant class {name}'
            )

        if __debug__:
            if not '__setattr__' in attrs:
                attrs['__setattr__'] = _default__setattr__

            attrs['_ezcontract_in__init__method'] = True
            attrs['__init__'] = _wrap__init__(attrs.get('__init__',
                                              _super__init__))

            if check_init:
                predicate = Invariant.identity_predicate
            else:
                predicate = Invariant._in__init__predicate

            attrs['__setattr__'] = _make_invariant(
                attrs['__setattr__'], predicate=predicate,
            )

            if '__next__' in attrs and '__iter__' in attrs:
                # support __invariant__ for iterators
                attrs['__next__'] = _make_invariant(attrs['__next__'])

        return super(Invariant, cls).__new__(cls, name, bases, attrs)