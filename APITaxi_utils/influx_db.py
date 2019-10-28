#coding: utf-8
from flask import current_app
from influxdb import InfluxDBClient
from datetime import datetime
import hashlib

def get_client(dbname=None):
    c = current_app.config
    config = dict([(k, c.get('INFLUXDB_{}'.format(k.upper()), None)) for k in\
        ['host', 'port', 'username', 'password', 'ssl', 'verify_ssl', 'timeout',
            'use_udp', 'udp_port']])
    if not config['host']:
        return None
    config['database'] = dbname
    return InfluxDBClient(**config)


def write_point(db, measurement, tags, value=1):
    client = get_client(db)
    if not client:
        return
    try:
        client.write_points([{
            "measurement": measurement,
            "tags": tags,
            "time": datetime.utcnow().strftime('%Y%m%dT%H:%M:%SZ'),
            "fields": {
                "value": value
            }
            }])
    except Exception as e:
        current_app.logger.error('Influxdb Error: {}'.format(e))


def write_get_taxis(zupc_insee, lon, lat, moteur, request, l_taxis):
        write_point(
            current_app.config['INFLUXDB_TAXIS_DB'],
            "get_taxis_requests",
            {
                "zupc": zupc_insee,
                "position": "{:.3f}:{:.3f}".format(float(lon), float(lat)),
                "moteur": moteur,
                "customer": hashlib.sha224(str(
                    (
                        request.headers.getlist("X-Forwarded-For")[0].rpartition(' ')[-1]
                        if 'X-Forwarded-For' in request.headers
                        else request.remote_addr
                                         ) or 'untrackable'
                                        ).encode('utf-8')
                                 ).hexdigest()[:10]
            },
            value=l_taxis
        )
