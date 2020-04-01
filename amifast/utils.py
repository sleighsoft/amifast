class cached_property(object):
    """A decorator that caches the return value on the first call of the
    function. Consecutive calls will get the cached result without running
    the function again.

    Decorated functions will also be marked as immutable similar to `@property`
    and as such cannot be changed with `obj.function_name = value`.

    The cache can be invalidated by `del obj.__dict__[function_name]`.
    """

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        if doc is None and fget is not None:
            doc = fget.__doc__
        self.__doc__ = doc

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError("Unreadable attribute")
        if self.fget.__name__ in obj.__dict__:
            return obj.__dict__[self.fget.__name__]
        value = obj.__dict__[self.fget.__name__] = self.fget(obj)
        return value

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("Can't set attribute")
        self.fset(obj, value)
