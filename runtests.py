#!/usr/bin/env python

# Application test settings

from django_replicated2.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
    'slave1': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'TEST_MIRROR': 'default',
    },
    'slave2': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'TEST_MIRROR': 'default',
    }
}

INSTALLED_APPS = ['django_replicated2']

DATABASE_ROUTERS = ['django_replicated2.routers.ReplicationRouter']

MIDDLEWARE_CLASSES = [
    'django_replicated2.middleware.ReplicationMiddleware',
]


# Configure settings

import sys
from django.conf import settings

settings.configure(**dict([(k,v) for k,v in globals().items() if k.isupper()]))

# setup.py test runner
def runtests():
    from django.test.utils import get_runner

    test_runner = get_runner(settings)(verbosity=1, interactive=True, failfast=False)
    failures = test_runner.run_tests(INSTALLED_APPS)
    sys.exit(failures)


if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv[:1] + ['test'] + sys.argv[1:])
