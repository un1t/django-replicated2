# coding: utf-8


class ReplicationMiddleware(object):
    # see http://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html#sec9.1
    SAFE_HTTP_METHODS = set(['GET', 'HEAD', 'OPTIONS', 'TRACE'])
    COOKIE_NAME = 'just_updated'
    COOKIE_VALUE = 'yes'

    def process_request(self, request):
        router = self.get_router()
        if router:
            if self.COOKIE_NAME in request.COOKIES:
                router.disable_slaves()
            elif request.method not in self.SAFE_HTTP_METHODS:
                router.disable_slaves()
            else:
                router.enable_slaves()

    def process_response(self, request, response):
        router = self.get_router()
        if router:
            if request.method not in self.SAFE_HTTP_METHODS and router.is_db_recently_updated():
                response.set_cookie(self.COOKIE_NAME, self.COOKIE_VALUE, max_age=router.replication_interval)
        return response

    def get_router(self):
        if not hasattr(self, '_router'):
            from django import db
            from django_replicated.routers import ReplicationRouter
            try:
                self._router = [router for router in db.router.routers if isinstance(router, ReplicationRouter)][0]
            except IndexError:
                self._router = None
        return self._router
