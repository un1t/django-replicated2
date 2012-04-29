from django.test import TestCase
from flexmock import flexmock
from django_replicated.tests.utils import override_settings

from django_replicated.pingers import DjangoDbPinger


class DjangoDbPingerTest(TestCase):

    def setUp(self):
        self.pinger = DjangoDbPinger()
        self.pinger.connections = {
                'slave1': flexmock(connection=None).should_receive('cursor').mock,
                'slave2': flexmock(connection=None).should_receive('cursor').and_raise(Exception()).mock
        }

    def test_should_check_alive(self):
        self.assertTrue(self.pinger.is_alive('slave1'))

    def test_should_check_dead_connection(self):
        self.assertFalse(self.pinger.is_alive('slave2'))


class DjangoDbPinger1Test(TestCase):

    def setUp(self):
        self.pinger = DjangoDbPinger()
        self.pinger.connections = {
                'slave1': flexmock(connection=flexmock().should_receive('ping').mock),
                'slave2': flexmock(connection=flexmock().should_receive('ping').and_raise(Exception()).mock)
        }

    def test_should_check_alive(self):
        self.assertTrue(self.pinger.is_alive('slave1'))

    def test_should_check_dead_connection(self):
        self.assertFalse(self.pinger.is_alive('slave2'))


class DjangoDbPingerCacheTest(TestCase):

    def test_should_cache_dead_connection(self):
        pinger = DjangoDbPinger()
        pinger.connections = {
                'slave2': flexmock(connection=flexmock().should_receive('ping').once.and_raise(Exception()).mock)
        }
        self.assertFalse(pinger.is_alive('slave2'))
        self.assertFalse(pinger.is_alive('slave2'))

    def test_should_not_cache_alive_connection(self):
        pinger = DjangoDbPinger()
        pinger.connections = {
                'slave2': flexmock(connection=flexmock().should_receive('ping').twice.mock)
        }
        self.assertTrue(pinger.is_alive('slave2'))
        self.assertTrue(pinger.is_alive('slave2'))

    @override_settings(DATABASE_DOWNTIME=5)
    def test_should_invalidate_dead_connection_sometimes(self):
        connection_ping = flexmock().should_receive('ping').and_raise(Exception())
        pinger = DjangoDbPinger()
        pinger.connections = {
                'slave2': flexmock(connection=connection_ping.mock)
        }

        flexmock(pinger).should_receive('time').and_return(1)
        pinger.is_alive('slave2')
        self.assertEquals(1, connection_ping.times_called)

        flexmock(pinger).should_receive('time').and_return(5)
        pinger.is_alive('slave2')
        self.assertEquals(1, connection_ping.times_called)

        flexmock(pinger).should_receive('time').and_return(6)
        pinger.is_alive('slave2')
        self.assertEquals(2, connection_ping.times_called)
