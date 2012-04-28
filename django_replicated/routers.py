# -*- coding:utf-8 -*-
import random
import time
from django.conf import settings

from django_replicated.pingers import DjangoDbPinger


class ReplicationRouter(object):
    REPLICATION_INTERVAL = 5

    def __init__(self):
        from django.db.utils import DEFAULT_DB_ALIAS
        self.DEFAULT_DB_ALIAS = DEFAULT_DB_ALIAS
        self.state = 'master'
        self.last_update = 0
        self.pinger = DjangoDbPinger()
        
    def get_state(self):
        return self.state
        
    def set_state(self, state):
        self.state = state

    # django-preferences
    # bug https://code.djangoproject.com/ticket/14849
    def allow_relation(self, obj1, obj2, **hints):
        return True

    def db_for_write(self, model, **hints):
        self.last_update = time.time()
        self.set_state('master')
        return self.DEFAULT_DB_ALIAS

    def db_for_read(self, model, **hints):
        if self.get_state() == 'master':
            return self.db_for_write(model, **hints)
        
        slaves = getattr(settings, 'DATABASE_SLAVES', [self.DEFAULT_DB_ALIAS])
        random.shuffle(slaves)
        for slave in slaves:
            if self.pinger.is_alive(slave):
                return slave
        else:
            return self.DEFAULT_DB_ALIAS

    def is_db_recently_updated(self):
        return time.time() - self.last_update < self.REPLICATION_INTERVAL
