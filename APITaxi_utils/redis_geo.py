# -*- coding: utf-8 -*-
from redis import StrictRedis
from redis.exceptions import ResponseError

class GeoRedis(StrictRedis):
    def geoadd(self, geoset, lat, lon, id_):
        return self.execute_command("geoadd {geoset} {lat} {lon} {id_}".format(
            geoset=geoset, lat=lat, lon=lon, id_=id_))

    def georadius(self, geoset, lat, lon, radius=15, units='km',
            withdistance=True, withcoordinates=True, withhash=False,
            withgeojson=False, withgeojsoncollection=False,
            noproperties=False, order='asc', storekey=None, storedistkey=None,
            version=3.2):
        command = 'georadius {geoset} {lat} {lon} {radius} {units}'.format(
                geoset=geoset, lat=lat, lon=lon, radius=radius, units=units)
        if withdistance and not storekey and not storedistkey:
            command += ' withdist' if version == 3.2 else ' withdistance'
        if withcoordinates and not storekey and not storedistkey:
            command += ' withcoord' if version == 3.2 else ' withcoordinates'
        if withhash:
            command += ' withhash'
        if withgeojson:
            command += ' withgeojson'
        if withgeojsoncollection:
            command += ' withgeojsoncollection'
        if noproperties:
            command += ' noproperties'
        command += ' '+order
        if storekey and version == 3.2:
            command += ' store {}'.format(storekey)
        if storedistkey and version == 3.2:
            command += ' storedist {}'.format(storedistkey)
        from flask import current_app
        try:
            if version == 3.2 or (not storekey and not storedistkey):
                return self.execute_command(command)
            else:
                r = self.execute_command(command)
                if len(r) == 0:
                    return []
                return self.zadd(storekey or storedistkey,
                            **{id_:d for id_, d, _ in r})
        except ResponseError as e:
            if version != 3.2:
                raise e
            self.georadius(geoset, lat, lon, radius, units, withdistance,
                withcoordinates, withhash, withgeojson, withgeojsoncollection,
                noproperties, order, storekey, storedistkey, 2.8)

    def geopos(self, key, *members):
        try:
            return self.execute_command('geopos {} {}'.format(key,
                 " ".join(map(str, members))))
        except ResponseError:
            taxi_score = self.zscore(key,
                 '{}'.format(" ".join(map(str, members))))
            if not taxi_score:
                return None
            r = self.execute_command('geodecode {}'.format(int(taxi_score)))
            return r if r else None



