from django.test import TestCase
from django.db import models, utils as db_utils
from django_replicated2.tests.utils import override_settings
from flexmock import flexmock

from django_replicated2.routers import ReplicationRouter


class Book(models.Model):
    pass


class DatabaseForWriteTest(TestCase):

    def test_should_return_default_database(self):
        router = ReplicationRouter()
        self.assertEquals(db_utils.DEFAULT_DB_ALIAS, router.db_for_write(Book),
                "expect database for write is default (master)")


class DatabaseForReadTest(TestCase):

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        },
    }

    DATABASES_WITH_SLAVES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        },
        'slave1': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
            'TEST_MIRROR': 'default',
        },
        'slave2': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
            'TEST_MIRROR': 'default',
        }
    }
    @override_settings(DATABASES=DATABASES_WITH_SLAVES)
    def test_should_return_random_slave(self):
        pinger = flexmock()
        pinger.should_receive('is_alive').with_args('slave1').and_return(True)
        pinger.should_receive('is_alive').with_args('slave2').and_return(True)

        router = ReplicationRouter()
        flexmock(router).should_receive('get_pinger').and_return(pinger)

        sequence1 = [router.db_for_read(Book) for n in range(0, 20)]
        sequence2 = [router.db_for_read(Book) for n in range(0, 20)]

        self.assertEquals(set(['slave1', 'slave2']), set(sequence1),
                "expect that sequence1 contans slaves only")
        self.assertEquals(set(['slave1', 'slave2']), set(sequence2),
                "expect that sequence2 contans slaves only")
        self.assertNotEquals(sequence1, sequence2,
                "random sequences could not to be equal")

    @override_settings(DATABASES=DATABASES)
    def test_should_not_to_suggest_database_when_slaves_does_not_defined(self):
        router = ReplicationRouter()
        self.assertEquals(router.db_for_read(Book), None)


    @override_settings(DATABASES=DATABASES_WITH_SLAVES)
    def test_should_check_slaves_is_alive(self):
        pinger = flexmock()
        pinger.should_receive('is_alive').with_args('slave1').and_return(True)
        pinger.should_receive('is_alive').with_args('slave2').and_return(False)

        router = ReplicationRouter()
        flexmock(router).should_receive('get_pinger').and_return(pinger)
        sequence1 = [router.db_for_read(Book) for n in range(0, 20)]
        self.assertEquals(set(['slave1']), set(sequence1),
                "expect that sequence1 contans alive slaves only")
