import sys
if sys.version_info[0] == 3:
    unicode = str

from django.test import TestCase
from sample.models import Chapter, Book, Author, StaffAuthor, Review
from a_sample.models import BookProxy


class SimpleTest(TestCase):
    def test_aldjemy_initialization(self):
        self.assertTrue(Chapter.sa)
        self.assertTrue(Book.sa)
        self.assertTrue(Author.sa)
        self.assertTrue(StaffAuthor.sa)
        self.assertTrue(Review.sa)
        self.assertTrue(BookProxy.sa)

    def test_engine_override_test(self):
        from aldjemy import core
        self.assertEquals(core.get_connection_string(), 'sqlite+pysqlite://')

    def test_querying(self):
        Book.objects.create(title='book title')
        Book.objects.all()
        self.assertEqual(Book.sa.query().count(), 1)


class AliasesTest(TestCase):
    multi_db = True

    def test_engines_cache(self):
        from aldjemy.core import Cache, get_engine

        self.assertEqual(get_engine('default'), Cache.engines['default'])
        self.assertEqual(get_engine('logs'), Cache.engines['logs'])
        self.assertEqual(get_engine(), Cache.engines['default'])
        self.assertNotEqual(get_engine('default'), get_engine('logs'))

    def test_sessions(self):
        from aldjemy.orm import get_session
        from django.db import connections
        session_default = get_session()
        session_default2 = get_session('default')
        self.assertEqual(session_default, session_default2)
        session_logs = get_session('logs')
        self.assertEqual(connections['default'].sa_session, session_default)
        self.assertEqual(connections['logs'].sa_session, session_logs)
        self.assertNotEqual(session_default, session_logs)

    def test_logs(self):
        from sample.models import Log
        Log.objects.create(record='1')
        Log.objects.create(record='2')
        self.assertEqual(Log.objects.using('logs').count(), 2)
        self.assertEqual(Log.sa.query().count(), 2)
        self.assertEqual(Log.sa.query().all()[0].record, '1')


class AldjemyMetaTests(TestCase):
    multi_db = True

    def test_meta(self):
        from sample.models import Log
        Log.objects.create(record='foo')

        foo = Log.sa.query().one()
        self.assertEqual(unicode(foo), 'foo')
        self.assertEqual(foo.reversed_record, 'oof')
        self.assertFalse(hasattr(foo, 'this_is_not_copied'))
