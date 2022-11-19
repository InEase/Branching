from functools import partial, wraps
from typing import Callable

_ON = True


def Toggle():
    global _ON
    _ON = not _ON


def Off():
    global _ON
    _ON = False


def On():
    global _ON
    _ON = True


def call_function(target: Callable, arguments: dict, result=None):
    # First Try passing all arguments
    if result is not None:
        arguments["_result"] = result
    try:
        return target(**arguments)
    except TypeError:
        # Then Try passing only the arguments that are defined in the function
        arguments = {k: v for k, v in arguments.items() if k in target.__code__.co_varnames}
        return target(**arguments)


class Wrapper:
    def __init__(self, function, in_class=False):
        self.function = function
        self._before = []
        self._after = []
        self.in_class = in_class

    def __call__(self, *args, **kwargs):
        var_names = self.function.__code__.co_varnames

        kwargs.update(zip(var_names, args))

        if _ON:
            for before_function in self._before:
                updates = call_function(before_function, kwargs)
                if updates:
                    kwargs.update(updates)

            result = call_function(self.function, kwargs)

            for after_function in self._after:
                result = call_function(after_function, kwargs, result=result)

            return result
        else:
            return call_function(self.function, kwargs)

    def remove_hook(self, function):
        if function in self._before:
            self._before.remove(function)
        elif function in self._after:
            self._after.remove(function)

    def before(self, function=None, *, order=0):
        if function is None:
            return partial(self.before, order=order)
        function.order = order
        self._before.append(function)
        self._before = sorted(self._before, key=lambda x: x.order)
        function.remove = partial(self.remove_hook, function)
        function.mount = partial(self.before, function)
        return function

    def after(self, function=None, *, order=0):
        if function is None:
            return partial(self.after, order=order)
        function.order = order
        self._after.append(function)
        self._after = sorted(self._after, key=lambda x: x.order)
        function.remove = partial(self.remove_hook, function)
        function.mount = partial(self.after, function)
        return function


def Plugin(function=None):
    # whether function is defined inside class
    if function.__name__ != function.__qualname__:
        wrapper = Wrapper(function, in_class=True)
    else:
        wrapper = Wrapper(function)

    @wraps(function)
    def inner(*args, **kwargs):
        return wrapper(*args, **kwargs)

    inner.before = wrapper.before
    inner.after = wrapper.after

    return inner
