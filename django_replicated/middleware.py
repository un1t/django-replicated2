# coding: utf-8
from django import db
from django_replicated.routers import ReplicationRouter


def get_router():
    try:
        return [router for router in db.router.routers if isinstance(router, ReplicationRouter)][0]
    except IndexError:
        return None


class ReplicationMiddleware(object):
    # see http://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html#sec9.1
    SAFE_HTTP_METHODS = set(['GET', 'HEAD', 'OPTIONS', 'TRACE'])
    COOKIE_NAME = 'just_updated'
    COOKIE_VALUE = 'yes'

    def process_request(self, request):
        router = get_router()
        if router:
            if self.COOKIE_NAME in request.COOKIES:
                state = 'master'
            elif request.method not in self.SAFE_HTTP_METHODS:
                state = 'master'
            else:
                state = 'slave'

            router.set_state(state)

    def process_response(self, request, response):
        router = get_router()
        if router:
            if request.method not in self.SAFE_HTTP_METHODS and router.is_db_recently_updated():
                response.set_cookie(self.COOKIE_NAME, self.COOKIE_VALUE, max_age=router.REPLICATION_INTERVAL)

        return response
