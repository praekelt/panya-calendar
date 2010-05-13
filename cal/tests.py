from datetime import datetime, timedelta
import unittest

from cal import models
from content.models import ModelBase

class EntrySaveHandlersTestCase(unittest.TestCase):
    def setUp(self):
        content = ModelBase()
        content.save()

        entry = models.Entry(
            start=datetime.now(), 
            end=datetime.now() + timedelta(days=1),
            repeat="does_not_repeat",
            content=content,
        )
        entry.save()
        self.entry = entry

    def test_save_handler_does_not_repeat(self):
        # raise an exception if handler is used with incorrect entry
        self.entry.repeat="daily"
        self.entry.save()
        #self.failUnlessRaises(Exception, models.save_handler_does_not_repeat, entry)
