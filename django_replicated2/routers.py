import random
import time
from django.conf import settings
from django.db import utils as db_utils


class ReplicationRouter(object):

    def __init__(self):
        self.is_slaves_enabled = True
        self.last_update_time = 0
        self.master_db_alias = db_utils.DEFAULT_DB_ALIAS
        self.slave_db_aliases = [db_alias
                for db_alias, params in settings.DATABASES.items()
                if params.get('TEST_MIRROR') == self.master_db_alias]
        self.replication_interval = settings.DATABASE_REPLICATION_INTERVAL

    def allow_relation(self, obj1, obj2, **hints):
        # XXX: it was misstake https://code.djangoproject.com/ticket/14849
        # XXX: should we check objects are really belongs to master or slaves???
        return True # allow relation for any replica

    def db_for_write(self, model, **hints):
        self.last_update_time = time.time()
        return self.master_db_alias

    def db_for_read(self, model, **hints):
        if not self.is_slaves_enabled:
            return self.master_db_alias

        if self.is_db_recently_updated():
            return self.master_db_alias

        pinger = self.get_pinger()
        random.shuffle(self.slave_db_aliases)
        for slave_db_alias in self.slave_db_aliases:
            if pinger.is_alive(slave_db_alias):
                return slave_db_alias

        return None # there is no suggestion

    def enable_slaves(self):
        self.is_slaves_enabled = True

    def disable_slaves(self):
        self.is_slaves_enabled = False

    def is_db_recently_updated(self):
        return time.time() - self.last_update_time < self.replication_interval

    def get_pinger(self):
        if not hasattr(self, '_pinger'):
            from django_replicated2.pingers import DjangoDbPinger
            self._pinger = DjangoDbPinger()
        return self._pinger
