import time
from django.conf import settings


class DjangoDbPinger(object):

    def __init__(self):
        from django.db import connections
        self.connections = connections
        self.downtime = getattr(settings, 'DATABASE_DOWNTIME', 60)
        self.dead_connections = {}

    def is_alive(self, db_alias):
        death_time = self.dead_connections.get(db_alias)

        if death_time:
            if death_time + self.downtime > self.time():
                return False
            else:
                del self.dead_connections[db_alias]

        db = self.connections[db_alias]

        try:
            if db.connection is not None and hasattr(db.connection, 'ping'):
                db.connection.ping()
            else:
                db.cursor()
            return True
        except StandardError:
            self.dead_connections[db_alias] = self.time()
            return False

    def time(self):
        return time.time()
