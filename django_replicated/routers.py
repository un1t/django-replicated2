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
        self.state = 'slave' # XXX: it was 'master', write a test
        self.last_update_time = 0
        self.pinger = DjangoDbPinger()
        
    def get_state(self):
        return self.state
        
    def set_state(self, state):
        self.state = state

    def allow_relation(self, obj1, obj2, **hints):
        # XXX: it was misstake https://code.djangoproject.com/ticket/14849
        # XXX: should we check objects are really belongs to master or slaves???
        return True # allow relation for any replica

    def db_for_write(self, model, **hints):
        self.last_update_time = time.time()
        return self.DEFAULT_DB_ALIAS

    def db_for_read(self, model, **hints):
        # XXX: omit to compare string literals
        if self.get_state() == 'master' or self.is_db_recently_updated():
            return self.DEFAULT_DB_ALIAS
        
        # XXX: this changes the list globally in the settings module
        slaves = getattr(settings, 'DATABASE_SLAVES', [])
        random.shuffle(slaves)
        for slave in slaves:
            if self.pinger.is_alive(slave):
                return slave

        return None # no suggestion

    def is_db_recently_updated(self):
        return time.time() - self.last_update_time < self.REPLICATION_INTERVAL
