from django.conf import settings
from django.test.utils import override_settings as _override_settings

def invalidate_routers():
    from django.db import router
    router.__init__(settings.DATABASE_ROUTERS)

def override_settings(**params):
    def wrap(f):
        @_override_settings(**params)
        def call(*args, **kwargs):
            invalidate_routers()
            return f(*args, **kwargs)
        return call
    return wrap


