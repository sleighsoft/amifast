import inspect


def test():
    a = 1
    b = 2
    c = 3


print(inspect.getfile(test))
print(inspect.getsourcefile(test))
print(inspect.getsourcelines(test))

print(inspect.getsourcefile(int))
