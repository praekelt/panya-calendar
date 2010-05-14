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

    def test_save_handler_does_not_repeat(self):
        # create an entry
        entry = models.Entry(
            start=datetime.now(), 
            end=datetime.now() + timedelta(days=1),
            repeat="does_not_repeat",
            content=self.content,
        )
        entry.save()
        entry.calendars.add(self.calendar)

        # raise an exception if handler is used with incorrect entry
        entry.repeat="daily"
        self.failUnlessRaises(Exception, models.save_handler_does_not_repeat, entry)
        entry.repeat="does_not_repeat"

        # should create a single entryitem linked to this entry
        models.save_handler_does_not_repeat(entry)
        entries = models.EntryItem.objects.filter(entry=entry)
        self.failUnlessEqual(entries.get().entry, entry)
        
        # created entry item should point to entry
        ent = entries.get()
        self.failUnlessEqual(ent.entry, entry)

        # created entry item should have same field values as entry
        self.failUnlessEqual(ent.start, entry.start)
        self.failUnlessEqual(ent.end, entry.end)
        self.failUnlessEqual(ent.content, entry.content)
        self.failUnlessEqual(ent.entry, entry)
        self.failUnlessEqual(list(ent.calendars.all()), list(entry.calendars.all()))

        # subsequent save should still only have a single entryitem linked to this entry 
        models.save_handler_does_not_repeat(entry)
        entries = models.EntryItem.objects.filter(entry=entry)
        self.failUnlessEqual(entries.get().entry, entry)
    
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
        entry.repeat_until = (entry.start + timedelta(days=30)).date()
        models.save_handler_daily(entry)
        entries = models.EntryItem.objects.filter(entry=entry)
        self.failUnlessEqual(entries.count(), 31)

        # check correct generation
        starts = set()
        entries = entries.order_by('start')
        for ent in entries:
            starts.add(ent.start)
            
            # entry end values should be start adjusted by original duration 
            self.failUnlessEqual(ent.duration, entry.duration)
        
            # created entry item should point to entry
            self.failUnlessEqual(ent.entry, entry)
        
            # created entry items should have same field values as entry (except for repeating start and ends)
            self.failUnlessEqual(ent.content, entry.content)
            self.failUnlessEqual(list(ent.calendars.all()), list(entry.calendars.all()))

        # entry items should not have the same starts
        self.failUnlessEqual(len(starts), 31)
           
        # subsequent save should still only create an entryitem linked to this entry for each day until entry's repeat until value.
        models.save_handler_daily(entry)
        entries = models.EntryItem.objects.filter(entry=entry)
        self.failUnlessEqual(entries.count(), 31)
    
    def test_save_handler_weekdays(self):
        handler = models.save_handler_weekdays
        # create an entry
        entry = models.Entry(
            start=datetime(year=2000, month=1, day=1, hour=1, minute=1), 
            end=datetime(year=2000, month=1, day=1, hour=1, minute=1) + timedelta(days=1),
            repeat="weekdays",
            repeat_until = (datetime.now() + timedelta(days=30)).date(),
            content=self.content,
        )
        entry.save()
        entry.calendars.add(self.calendar)
        
        # raise an exception if handler is used with incorrect entry
        entry.repeat = 'does_not_repeat'
        self.failUnlessRaises(Exception, handler, entry)
        entry.repeat='weekdays'
        
        # raise an exception if entry does not provide repeat until
        entry.repeat_until = None
        self.failUnlessRaises(Exception, handler, entry)
        
        # should create an entryitem linked to this entry for each weekday until entry's repeat until value.
        entry.repeat_until = (entry.start + timedelta(days=30)).date()
        handler(entry)
        entries = models.EntryItem.objects.filter(entry=entry)
        self.failUnlessEqual(entries.count(), 21)
        
        # check correct generation
        starts = set()
        for ent in entries:
            starts.add(ent.start)
            
            # only weekdays
            self.failIf(ent.start.weekday() >= 5)
            
            # entry end values should be start adjusted by original duration 
            self.failUnlessEqual(ent.duration, entry.duration)
        
            # created entry item should point to entry
            self.failUnlessEqual(ent.entry, entry)
        
            # created entry items should have same field values as entry (except for repeating start and ends)
            self.failUnlessEqual(ent.content, entry.content)
            self.failUnlessEqual(list(ent.calendars.all()), list(entry.calendars.all()))
        
        # entry items should not have the same starts
        self.failUnlessEqual(len(starts), 21)
        
        # subsequent save should still only create an entryitem linked to this entry for each weekday until entry's repeat until value.
        handler(entry)
        entries = models.EntryItem.objects.filter(entry=entry)
        self.failUnlessEqual(entries.count(), 21)
    
    def test_save_handler_weekends(self):
        handler = models.save_handler_weekends
        # create an entry
        entry = models.Entry(
            start=datetime(year=2000, month=1, day=1, hour=1, minute=1), 
            end=datetime(year=2000, month=1, day=1, hour=1, minute=1) + timedelta(days=1),
            repeat="weekends",
            repeat_until = (datetime.now() + timedelta(days=30)).date(),
            content=self.content,
        )
        entry.save()
        entry.calendars.add(self.calendar)
        
        # raise an exception if handler is used with incorrect entry
        entry.repeat = 'does_not_repeat'
        self.failUnlessRaises(Exception, handler, entry)
        entry.repeat='weekends'
        
        # raise an exception if entry does not provide repeat until
        entry.repeat_until = None
        self.failUnlessRaises(Exception, handler, entry)
        
        # should create an entryitem linked to this entry for each weekend day until entry's repeat until value.
        entry.repeat_until = (entry.start + timedelta(days=30)).date()
        handler(entry)
        entries = models.EntryItem.objects.filter(entry=entry)
        self.failUnlessEqual(entries.count(), 10)
        
        # check correct generation
        starts = set()
        for ent in entries:
            starts.add(ent.start)
            
            # only weekend days
            self.failIf(ent.start.weekday() < 5)
            
            # entry end values should be start adjusted by original duration 
            self.failUnlessEqual(ent.duration, entry.duration)
        
            # created entry item should point to entry
            self.failUnlessEqual(ent.entry, entry)
        
            # created entry items should have same field values as entry (except for repeating start and ends)
            self.failUnlessEqual(ent.content, entry.content)
            self.failUnlessEqual(list(ent.calendars.all()), list(entry.calendars.all()))
        
        # entry items should not have the same starts
        self.failUnlessEqual(len(starts), 10)
        
        # subsequent save should still only create an entryitem linked to this entry for each weekday until entry's repeat until value.
        handler(entry)
        entries = models.EntryItem.objects.filter(entry=entry)
        self.failUnlessEqual(entries.count(), 10)
    
    def test_save_handler_weekly(self):
        handler = models.save_handler_weekly
        # create an entry
        entry = models.Entry(
            start=datetime(year=2000, month=1, day=1, hour=1, minute=1), 
            end=datetime(year=2000, month=1, day=1, hour=1, minute=1) + timedelta(days=1),
            repeat="weekly",
            repeat_until = (datetime.now() + timedelta(days=30)).date(),
            content=self.content,
        )
        entry.save()
        entry.calendars.add(self.calendar)
        
        # raise an exception if handler is used with incorrect entry
        entry.repeat = 'does_not_repeat'
        self.failUnlessRaises(Exception, handler, entry)
        entry.repeat='weekly'
        
        # raise an exception if entry does not provide repeat until
        entry.repeat_until = None
        self.failUnlessRaises(Exception, handler, entry)
        
        # should create an entryitem linked to this entry for each week until entry's repeat until value, with the start day being the same for each week.
        entry.repeat_until = (entry.start + timedelta(days=30)).date()
        handler(entry)
        entries = models.EntryItem.objects.filter(entry=entry)
        self.failUnlessEqual(entries.count(), 5)
        
        # check correct generation
        starts = set()
        for ent in entries:
            starts.add(ent.start)
           
            # weekdays should be the same
            self.failUnlessEqual(ent.start.weekday(), entry.start.weekday())
       
            # entry end values should be start adjusted by original duration 
            self.failUnlessEqual(ent.duration, entry.duration)
        
            # created entry item should point to entry
            self.failUnlessEqual(ent.entry, entry)
        
            # created entry items should have same field values as entry (except for repeating start and ends)
            self.failUnlessEqual(ent.content, entry.content)
            self.failUnlessEqual(list(ent.calendars.all()), list(entry.calendars.all()))
        
        # entry items should not have the same starts
        self.failUnlessEqual(len(starts), 5)
        
        # subsequent save should still only create an entryitem linked to this entry for each weekday until entry's repeat until value.
        handler(entry)
        entries = models.EntryItem.objects.filter(entry=entry)
        self.failUnlessEqual(entries.count(), 5)
    
    def test_save_handler_monthly_by_day_of_month(self):
        handler = models.save_handler_monthly_by_day_of_month
        # create an entry
        entry = models.Entry(
            start=datetime(year=2000, month=1, day=31, hour=1, minute=1), 
            end=datetime(year=2000, month=2, day=1, hour=1, minute=1) + timedelta(days=1),
            repeat="monthly_by_day_of_month",
            repeat_until = (datetime.now() + timedelta(days=30)).date(),
            content=self.content,
        )
        entry.save()
        entry.calendars.add(self.calendar)
        
        # raise an exception if handler is used with incorrect entry
        entry.repeat = 'does_not_repeat'
        self.failUnlessRaises(Exception, handler, entry)
        entry.repeat='monthly_by_day_of_month'
        
        # raise an exception if entry does not provide repeat until
        entry.repeat_until = None
        self.failUnlessRaises(Exception, handler, entry)
        
        # should create an entryitem linked to this entry for each month until entry's repeat until value, with the start day being the same day date of the month for each month.
        entry.repeat_until = (entry.start + timedelta(days=366)).date()
        handler(entry)
        entries = models.EntryItem.objects.filter(entry=entry)
        self.failUnlessEqual(entries.count(), 7)
        
        # check correct generation
        starts = set()
        for ent in entries:
            starts.add(ent.start)
           
            # day dates should be the same
            self.failUnlessEqual(ent.start.day, entry.start.day)
       
            # entry end values should be start adjusted by original duration 
            self.failUnlessEqual(ent.duration, entry.duration)
        
            # created entry item should point to entry
            self.failUnlessEqual(ent.entry, entry)
        
            # created entry items should have same field values as entry (except for repeating start and ends)
            self.failUnlessEqual(ent.content, entry.content)
            self.failUnlessEqual(list(ent.calendars.all()), list(entry.calendars.all()))
        
        # entry items should not have the same starts
        self.failUnlessEqual(len(starts), 7)
        
        # subsequent save should still only create an entryitem linked to this entry for each month until entry's repeat until value, with the start day being the same day date of the month for each month.
        handler(entry)
        entries = models.EntryItem.objects.filter(entry=entry)
        self.failUnlessEqual(entries.count(), 7)
