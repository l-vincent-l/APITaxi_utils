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
            noproperties=False, order='asc', version=3.2):
        command = 'georadius {geoset} {lat} {lon} {radius} {units}'.format(
                geoset=geoset, lat=lat, lon=lon, radius=radius, units=units)
        if withdistance:
            command += ' withdist' if version == 3.2 else ' withdistance'
        if withcoordinates:
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
        try:
            return self.execute_command(command)
        except ResponseError as e:
            if version != 3.2:
                raise e
            self.georadius(geoset, lat, lon, radius, units, withdistance,
                withcoordinates, withhash, withgeojson, withgeojsoncollection,
                noproperties, order, 2.8)

    def geopos(self, key, *members):
        try:
            return self.execute_command('geopos {} {}'.format(key,
                 " ".join(map(str, members))))
        except ResponseError:
            r = self.zscore(key,
                 '{}'.format(" ".join(map(str, members))))
            r = self.geodecode(int(taxi_score)) if taxi_score else None
            return r[0] if r else None



