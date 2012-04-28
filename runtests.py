#!/usr/bin/env python
import os
import sys
from django.conf import settings

if __name__ == "__main__":
    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            },
            'slave': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS = ['django_replicated']
    )
    from django.core.management import execute_from_command_line

    print sys.argv
    execute_from_command_line(sys.argv[:1] + ['test'] + sys.argv[1:])
