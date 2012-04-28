#!/usr/bin/env python

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
    'slave': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

INSTALLED_APPS = ['django_replicated']


if __name__ == "__main__":
    import sys
    from django.conf import settings
    from django.core.management import execute_from_command_line

    settings.configure(**dict([(k,v) for k,v in globals().items() if k.isupper()]))
    execute_from_command_line(sys.argv[:1] + ['test'] + sys.argv[1:])
