from dogpile.cache.backends import Redis

class RedisWithoutPickleBackend(Redis):
    def get(self, key):
        value = self.client.get(key)
        if value is None:
            return NO_VALUE
        return value

    def get_multi(self, keys):
        if not keys:
            return []
        values = self.client.mget(keys)
        return [v if v is not None else NO_VALUE for v in values]

    def set(self, key, value):
        if self.redis_expiration_time:
            self.client.setex(key, self.redis_expiration_time, value)
        else:
            self.client.set(key, value)

    def set_multi(self, mapping):
        if not self.redis_expiration_time:
            self.client.mset(mapping)
        else:
            pipe = self.client.pipeline()
            for key, value in list(mapping.items()):
                pipe.setex(key, self.redis_expiration_time, value)
            pipe.execute()
