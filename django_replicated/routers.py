# -*- coding:utf-8 -*-
import random
import time
from django.conf import settings


class ReplicationRouter(object):

    def __init__(self):
        from django.db import utils as db_utils
        from django_replicated.pingers import DjangoDbPinger

        self.last_update_time = 0
        self.master_db_alias = db_utils.DEFAULT_DB_ALIAS
        self.slave_db_aliases = [db_alias for db_alias, params in settings.DATABASES.items() if params.get('TEST_MIRROR') == self.master_db_alias]
        self.state = 'slave'
        self.pinger = DjangoDbPinger()
        self.replication_interval = settings.DATABASE_REPLICATION_INTERVAL

    def allow_relation(self, obj1, obj2, **hints):
        # XXX: it was misstake https://code.djangoproject.com/ticket/14849
        # XXX: should we check objects are really belongs to master or slaves???
        return True # allow relation for any replica

    def db_for_write(self, model, **hints):
        self.last_update_time = time.time()
        return self.master_db_alias

    def db_for_read(self, model, **hints):
        # XXX: omit to compare string literals
        if self.get_state() == 'master' or self.is_db_recently_updated():
            return self.master_db_alias

        random.shuffle(self.slave_db_aliases)
        for slave_db_alias in self.slave_db_aliases:
            if self.pinger.is_alive(slave_db_alias):
                return slave_db_alias

        return None # there is no suggestion

    def get_state(self):
        return self.state

    def set_state(self, state):
        self.state = state

    def is_db_recently_updated(self):
        return time.time() - self.last_update_time < self.replication_interval
