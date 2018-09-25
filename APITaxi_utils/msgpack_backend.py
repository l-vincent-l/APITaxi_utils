from dogpile.cache.proxy import ProxyBackend
import msgpack
from dogpile.cache.api import NO_VALUE, CachedValue
import datetime, time

class _EncodedProxy(ProxyBackend):
    """base class for building value-mangling proxies"""

    def value_decode(self, value):
        raise NotImplementedError("override me")

    def value_encode(self, value):
        raise NotImplementedError("override me")

    def set(self, k, v):
        v = self.value_encode(v)
        self.proxied.set(k, v)

    def get(self, key):
        v = self.proxied.get(key)
        return self.value_decode(v)

    def set_multi(self, mapping):
        """encode to a new dict to preserve unencoded values in-place when
           called by `get_or_create_multi`
           """
        mapping_set = {}
        for (k, v) in mapping.items():
            mapping_set[k] = self.value_encode(v)
        return self.proxied.set_multi(mapping_set)

    def get_multi(self, keys):
        results = self.proxied.get_multi(keys)
        translated = []
        for record in results:
            try:
                translated.append(self.value_decode(record))
            except Exception as e:
                raise
        return translated


def decode_datetime(obj):
    if b'__datetime__' in obj:
        return datetime.datetime.fromtimestamp(obj[b'as_int'])
    elif b'__date__' in obj:
        return datetime.date.fromordinal(obj[b'as_int'])
    return obj

def encode_datetime(obj):
    if isinstance(obj, datetime.datetime):
        obj = {'__datetime__': True, 'as_int': time.mktime(obj.timetuple())}
    elif isinstance(obj, datetime.date):
        obj = {'__date__': True, 'as_int': obj.toordinal()}
    return obj

class MsgpackProxy(_EncodedProxy):
    """custom decode/encode for value mangling"""

    def value_decode(self, v):
        if not v or v is NO_VALUE:
            return NO_VALUE
        # you probably want to specify a custom decoder via `object_hook`
        v = msgpack.unpackb(v, encoding="utf-8", object_hook=decode_datetime)
        return CachedValue(*v)

    def value_encode(self, v):
        # you probably want to specify a custom encoder via `default`
        return msgpack.packb(v, use_bin_type=True, default=encode_datetime)
