# -*- coding:utf-8 -*-
import random
import time
from datetime import datetime, timedelta

from django.conf import settings


class ReplicationRouter(object):
    REPLICATION_INTERVAL = 5

    def __init__(self):
        from django.db import connections
        from django.db.utils import DEFAULT_DB_ALIAS
        self.connections = connections
        self.DEFAULT_DB_ALIAS = DEFAULT_DB_ALIAS
        self.downtime = timedelta(seconds=getattr(settings, 'DATABASE_DOWNTIME', 60))
        self.dead_slaves = {}
        self.state = 'master'
        self.last_update = 0
        
    def get_state(self):
        return self.state
        
    def set_state(self, state):
        self.state = state

    def is_alive(self, slave):
        death_time = self.dead_slaves.get(slave)
        if death_time:
            if death_time + self.downtime > datetime.now():
                return False
            else:
                del self.dead_slaves[slave]
        db = self.connections[slave]
        try:
            if db.connection is not None and hasattr(db.connection, 'ping'):
                db.connection.ping()
            else:
                db.cursor()
            return True
        except StandardError:
            self.dead_slaves[slave] = datetime.now()
            return False

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
            if self.is_alive(slave):
                return slave
        else:
            return self.DEFAULT_DB_ALIAS

    def is_db_recently_updated(self):
        return time.time() - self.last_update < self.REPLICATION_INTERVAL
