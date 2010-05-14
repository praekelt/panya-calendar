from datetime import datetime, timedelta
import unittest

from cal import models
from content.models import ModelBase

class EntrySaveHandlersTestCase(unittest.TestCase):
    def setUp(self):
        content = ModelBase()
        content.save()
        self.content = content
        calendar = models.Calendar()
        calendar.save()
        self.calendar = calendar

        entry = models.Entry(
            start=datetime.now(), 
            end=datetime.now() + timedelta(days=1),
            repeat="does_not_repeat",
            content=content,
        )
        entry.save()
        entry.calendars.add(calendar)
        self.entry = entry

    def test_save_handler_does_not_repeat(self):
        # raise an exception if handler is used with incorrect entry
        self.entry.repeat="daily"
        self.failUnlessRaises(Exception, models.save_handler_does_not_repeat, self.entry)
        self.entry.repeat="does_not_repeat"

        # should create a single entryitem linked to this entry
        models.save_handler_does_not_repeat(self.entry)
        entries = models.EntryItem.objects.filter(entry=self.entry)
        self.failUnlessEqual(entries.get().entry, self.entry)
        
        # created entry item should point to entry
        entry = entries.get()
        self.failUnlessEqual(entry.entry, self.entry)

        # created entry item should have same field values as entry
        self.failUnlessEqual(entry.start, self.entry.start)
        self.failUnlessEqual(entry.end, self.entry.end)
        self.failUnlessEqual(entry.content, self.entry.content)
        self.failUnlessEqual(entry.entry, self.entry)
        self.failUnlessEqual(list(entry.calendars.all()), list(self.entry.calendars.all()))

        # subsequent save should still only have a single entryitem linked to this entry 
        models.save_handler_does_not_repeat(self.entry)
        entries = models.EntryItem.objects.filter(entry=self.entry)
        self.failUnlessEqual(entries.get().entry, self.entry)
    
    def test_save_handler_daily(self):
        # create an entry
        entry = models.Entry(
            start=datetime.now(), 
            end=datetime.now() + timedelta(days=1),
            repeat="daily",
            repeat_until = (datetime.now() + timedelta(days=30)).date(),
            content=self.content,
        )
        entry.save()
        entry.calendars.add(self.calendar)
        
        # raise an exception if handler is used with incorrect entry
        entry.repeat = 'does_not_repeat'
        self.failUnlessRaises(Exception, models.save_handler_daily, entry)

        # raise an exception if entry does not provide repeat until
        entry.repeat='daily'
        entry.repeat_until = None
        self.failUnlessRaises(Exception, models.save_handler_daily, entry)

        # should create an entryitem linked to this entry for each day until entry's repeat until value.
        entry.repeat_until = (datetime.now() + timedelta(days=30)).date()
        models.save_handler_daily(entry)
        entries = models.EntryItem.objects.filter(entry=entry)
        self.failUnlessEqual(entries.count(), 30)

        # check correct generation
        entries = entries.order_by('start')
        i = 0
        duration = entry.end - entry.start
        for ent in entries:
            if i != 0:
                # all entry start values should be seperated by a day
                self.failUnlessEqual(ent.start, entries[i - 1].start + timedelta(days=1))
            i += 1
            # entry end values should be start adjusted by original duration 
            self.failUnlessEqual(ent.end - ent.start, duration)
        
            # created entry item should point to entry
            self.failUnlessEqual(ent.entry, entry)
        
            # created entry items should have same field values as entry (except for repeating start and ends)
            self.failUnlessEqual(ent.content, entry.content)
            self.failUnlessEqual(list(ent.calendars.all()), list(entry.calendars.all()))
           
        # subsequent save should still only create an entryitem linked to this entry for each day until entry's repeat until value.
        models.save_handler_daily(entry)
        entries = models.EntryItem.objects.filter(entry=entry)
        self.failUnlessEqual(entries.count(), 30)
