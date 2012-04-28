from django.http import HttpResponseRedirect
from django.test import TestCase, RequestFactory
from flexmock import flexmock
from django_replicated.tests.utils import override_settings

from django_replicated.middleware import get_router, ReplicationMiddleware
from django_replicated.routers import ReplicationRouter


class GetRouterTest(TestCase):

    @override_settings(DATABASE_ROUTERS=['django_replicated.ReplicationRouter'])
    def test_should_return_replication_router(self):
        self.assertTrue(isinstance(get_router(), ReplicationRouter))

    @override_settings(DATABASE_ROUTERS=[])
    def test_should_return_none_when_no_routers_defined(self):
        self.assertTrue(get_router() is None)


class ReplicationMiddlewareHttpMethodsTest(TestCase):

    SETTINGS = dict(
            DATABASE_ROUTERS=['django_replicated.ReplicationRouter'],
    )

    def setUp(self):
        self.middleware = ReplicationMiddleware()
        self.request = RequestFactory()

    @override_settings(**SETTINGS)
    def test_get(self):
        flexmock(ReplicationRouter).should_receive('set_state').with_args('slave').once
        self.middleware.process_request(self.request.get('/'))

    @override_settings(**SETTINGS)
    def test_head(self):
        flexmock(ReplicationRouter).should_receive('set_state').with_args('slave').once
        self.middleware.process_request(self.request.head('/'))

    @override_settings(**SETTINGS)
    def test_options(self):
        flexmock(ReplicationRouter).should_receive('set_state').with_args('slave').once
        self.middleware.process_request(self.request.options('/'))

    @override_settings(**SETTINGS)
    def test_trace(self):
        flexmock(ReplicationRouter).should_receive('set_state').with_args('slave').once
        request = self.request.get('/')
        request.method = 'TRACE'
        self.middleware.process_request(request)

    @override_settings(**SETTINGS)
    def test_post(self):
        flexmock(ReplicationRouter).should_receive('set_state').with_args('master').once
        self.middleware.process_request(self.request.post('/'))

    @override_settings(**SETTINGS)
    def test_delete(self):
        flexmock(ReplicationRouter).should_receive('set_state').with_args('master').once
        self.middleware.process_request(self.request.delete('/'))

    @override_settings(**SETTINGS)
    def test_put(self):
        flexmock(ReplicationRouter).should_receive('set_state').with_args('master').once
        self.middleware.process_request(self.request.put('/'))


class ReplicationMiddlewareRecentlyUpdatedTest(TestCase):

    SETTINGS = dict(
            DATABASE_ROUTERS=['django_replicated.ReplicationRouter'],
    )

    def setUp(self):
        self.middleware = ReplicationMiddleware()
        self.request = RequestFactory()

    @override_settings(**SETTINGS)
    def test_process_request(self):
        self.request.cookies[ReplicationMiddleware.COOKIE_NAME] = 'any-value'
        flexmock(ReplicationRouter).should_receive('set_state').with_args('master').once
        self.middleware.process_request(self.request.get('/'))

    @override_settings(**SETTINGS)
    def test_process_response_updateable_methods(self):
        request = self.request.post('/')
        response = HttpResponseRedirect('/')
        flexmock(ReplicationRouter).should_receive('is_db_recently_updated').with_args().and_return(True)
        self.middleware.process_response(request, response)
        self.assertIn(ReplicationMiddleware.COOKIE_NAME, response.cookies)

    @override_settings(**SETTINGS)
    def test_process_response_safe_methods(self):
        request = self.request.get('/')
        response = HttpResponseRedirect('/')
        flexmock(ReplicationRouter).should_receive('is_db_recently_updated').with_args().and_return(True)
        self.middleware.process_response(request, response)
        self.assertNotIn(ReplicationMiddleware.COOKIE_NAME, response.cookies)
