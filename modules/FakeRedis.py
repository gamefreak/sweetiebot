import random
from fnmatch import fnmatch

def enc(string):
    # redis actually stores bytes, not strings
    if isinstance(string, bytes): return string
    return string.encode('utf-8')

class FakeRedis(object):
    def __init__(self):
        self.data = {}

    def set(self, key, value):
        key = enc(key)
        value = enc(value)
        self.data[key] = value

    def get(self, key):
        key = enc(key)
        if not key in self.data: return None
        return self.data[key]

    def keys(self, pattern):
        return [x for x in list(self.data.keys()) if fnmatch(x.decode('utf-8'), pattern)]

    def srandmember(self, key):
        key = enc(key)
        try:
            return random.choice(self.data[key])
        except KeyError:
            return None

    def sadd(self, key, value):
        key = enc(key)
        value = enc(value)
        if key in self.data:
            if value in self.data[key]:
                return 0
            self.data[key].append(value)
            return 1
        self.data[key] = [value]
        return 1

    def smembers(self, key):
        key = enc(key)
        if key in self.data:
            return self.data[key]
        return []

    def srem(self, key, value):
        key = enc(key)
        value = enc(value)
        if key in self.data:
            if value in self.data[key]:
                self.data[key].remove(value)
                return 1

    def scard(self, key):
        key = enc(key)
        return len(self.data[key])

    def hincrby(self, key, field, increment):
        key = enc(key)
        field = enc(field)
        if not key in self.data:
            self.data[key] = {}
        hash = self.data[key]
        if not field in hash:
            hash[field] = 0
        hash[field] += increment
        #print(key, '=', field, hash[field])

    def hgetall(self, key):
        key = enc(key)
        return self.data[key]

    def exists(self, key):
        key = enc(key)
        return key in self.data

