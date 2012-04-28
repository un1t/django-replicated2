# coding: utf-8
from django import db


def get_router():
    try:
        return db.router.routers[0]
    except IndexError:
        pass


class ReplicationMiddleware:
    HTTP_SAFE_METHODS = ['GET', 'HEAD', 'OPTION']

    def process_request(self, request):
        if request.COOKIES.get('just_updated') == 'true':
            state = 'master'
        elif request.method in self.HTTP_SAFE_METHODS:
            state = 'slave' 
        else:
            state = 'master'
        
        router = get_router()
        if router:
            router.set_state(state)

    def process_response(self, request, response):
        router = get_router()
        if router:
            if request.method not in self.HTTP_SAFE_METHODS and router.is_db_recently_updated():
                response.set_cookie('just_updated', 'true', max_age=router.REPLICATION_INTERVAL)

        return response
