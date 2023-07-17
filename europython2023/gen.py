def a():
    bret = yield from b()
    print(bret)
    dret = yield from d()
    print(dret)
    return "a is done"


def b():
    cret = yield from c()
    print(cret)
    return "b is done"


def c():
    yield 1
    yield 2
    yield 3
    return "c is done"


def d():
    yield 4
    yield 5
    return "d is done"



