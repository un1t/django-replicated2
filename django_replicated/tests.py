import unittest
from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings

from django_replicated.middleware import get_router, ReplicationRouter


class GetRouterTest(TestCase):

    @override_settings(DATABASE_ROUTERS=['django_replicated.ReplicationRouter'])
    def test_should_return_replication_router(self):
        self._invalidate_routers()
        self.assertTrue(isinstance(get_router(), ReplicationRouter))

    @override_settings(DATABASE_ROUTERS=[])
    def test_should_return_none_when_no_routers_defined(self):
        self._invalidate_routers()
        self.assertTrue(get_router() is None)

    def _invalidate_routers(self):
        from django.db import router
        router.__init__(settings.DATABASE_ROUTERS)
