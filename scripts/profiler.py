import copy
import numpy as np

class TimingNode:
    def __init__(self, times):
        self.times = times
        self.children = {}

    def set(self, names, time):
        if len(names) == 1:
            self.children[names[0]] = TimingNode(time)
        else:
            # Assume child exists
            self.children[names[0]].set(names[1:], time)

    def get(self, names):
        assert(len(names) > 0)
        if len(names) == 1:
            return self.children[names[0]]
        else:
            return self.children[names[0]].get(names[1:])

    def avg(self):
        return np.average(self.times)

    def stddev(self):
        return np.std(self.times)

def dicts_in_pairs(a, b):
    assert(a.keys() == b.keys())
    for key, value in a.items():
        yield value, b[key]

class ProfileData:
    def __init__(self, data):
        self.children = {}
        for line in data.splitlines():
            [key, times] = line.split(': ')
            times_ints = []
            for t in times.split(' '):
                assert(t[-2:] == 'µs')
                times_ints.append(int(t[:-2]))

            self.set(key.split('.'), times_ints)

    @staticmethod
    def read(path):
        with open(path) as f:
            return ProfileData(f.read())

    def set(self, names, time):
        assert(len(names) > 0)
        if len(names) == 1:
            self.children[names[0]] = TimingNode(time)
        else:
            # Assume child exists
            self.children[names[0]].set(names[1:], time)

    def get(self, names):
        assert(len(names) > 0)
        if len(names) == 1:
            return self.children[names[0]]
        else:
            return self.children[names[0]].get(names[1:])

    def get_by_key(self, key):
        return self.get(key.split('.'))

    def merge(self, other):
        def x(a, b):
            a.times += b.times
            for ac, bc in dicts_in_pairs(a.children, b.children):
                x(ac, bc)

        for a, b in dicts_in_pairs(self.children, other.children):
            x(a, b)

    @staticmethod
    def merge_all(items):
        assert(len(items) > 0)
        pd = copy.deepcopy(items[0])
        for item in items[1:]:
            pd.merge(item)
        return pd

    def __str__(self):
        stack = []
        def x(name, node):
            stack.append(name)
            out = ''
            for i, name in enumerate(stack):
                if i != 0:
                    out += '.'
                out += name
            out += ': ' + ' '.join([f'{time}µs' for time in node.times]) + '\n'
            for name, child in node.children.items():
                out += x(name, child)
            stack.pop()
            return out

        out = ''
        for name, child in self.children.items():
            out += x(name, child)

        return out[:-1]
