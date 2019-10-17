# -*- coding: utf-8 -*-

__author__ = 'Vincent Lara'
__contact__ = "vincent.lara@data.gouv.fr"
__homepage__ = "https://github.com/"
__version__ = '0.1.2'
__doc__ = "A set of utils function used by APITaxi"


get_columns_names = lambda m: [c.name for c in m.__table__.columns]
