# assorted sequence helpers

from heapq        import heapify, heappop, heappush

class PrioObj(object):
    def __init__(self, val, lt):
        self.val = val
        self.lt  = lt

    def __str__(self):
        return str(self.val)

    def __lt__(self, other):
        return self.lt(self.val, other.val)


def imerge(lt, *iters):
    nxtheap = []
    _lt = lambda a, b: lt(a[0], b[0])
    for i in iters:
        try:
            it = iter(i)
            nxtheap.append(PrioObj((next(it), it), _lt))
        except StopIteration:
            pass
    heapify(nxtheap)
    while nxtheap:
        wrapper = heappop(nxtheap)
        x, it = wrapper.val
        yield x
        try:
            wrapper.val = (next(it), it)
            heappush(nxtheap, wrapper)
        except StopIteration:
            pass

def uniq(seq):
    it = iter(seq)
    last = next(it)
    yield last
    for x in it:
        if x != last:
            last = x
            yield x
