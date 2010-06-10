from datetime import datetime, timedelta
import unittest

from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models as django_models


from cal import models
from cal.models import Calendar, Entry, EntryItem
from panya.models import ModelBase

class WantedContent(ModelBase):
    pass
django_models.register_models('cal', WantedContent)

class UnwantedContent(ModelBase):
    pass
django_models.register_models('cal', UnwantedContent)

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

class PermittedManagerTestCase(unittest.TestCase):
    def setUp(self):
        # create website site item and set as current site
        self.web_site = Site(domain="web.address.com")
        self.web_site.save()
        settings.SITE_ID = self.web_site.id

    def test_get_query_set(self):
        # create unpublished calendar
        unpublished_cal = Calendar(title='title', state='unpublished')
        unpublished_cal.save()
        unpublished_cal.sites.add(self.web_site)
        unpublished_cal.save()
        
        # create staging calendar
        staging_cal = Calendar(title='title', state='staging')
        staging_cal.save()
        staging_cal.sites.add(self.web_site)
        staging_cal.save()
        
        # create published calendar
        published_cal = Calendar(title='title', state='published')
        published_cal.save()
        published_cal.sites.add(self.web_site)
        published_cal.save()
        
        # create unpublished content
        unpublished_content = ModelBase(title='title', state='unpublished')
        unpublished_content.save()
        unpublished_content.sites.add(self.web_site)
        unpublished_content.save()
        
        # create staging content
        staging_content = ModelBase(title='title', state='staging')
        staging_content.save()
        staging_content.sites.add(self.web_site)
        staging_content.save()
        
        # create published content
        published_content = ModelBase(title='title', state='published')
        published_content.save()
        published_content.sites.add(self.web_site)
        published_content.save()

        # entries with unpublished calendars and content should not be available in queryset
        # create unpublished cal and content entries
        entry_obj = Entry(start=datetime.now(), end=datetime.now() + timedelta(days=1), repeat="daily", repeat_until=(datetime.now() + timedelta(days=30)).date(), content=unpublished_content)
        entry_obj.save()
        entry_obj.calendars.add(unpublished_cal)
        entry_obj.save()
        queryset = EntryItem.permitted.all()
        self.failIf(queryset.count())
        Entry.objects.all().delete()
        
        # entries with unpublished calendars should not be available in queryset, regardless of content state
        # create unpublished cal, published content entries
        entry_obj = Entry(start=datetime.now(), end=datetime.now() + timedelta(days=1), repeat="daily", repeat_until=(datetime.now() + timedelta(days=30)).date(), content=published_content)
        entry_obj.save()
        entry_obj.calendars.add(unpublished_cal)
        entry_obj.save()
        queryset = EntryItem.permitted.all()
        self.failIf(queryset.count())
        Entry.objects.all().delete()
        
        # entries with unpublished content should not be available in queryset, regardless of cal state
        # create unpublished content, published cal entries
        entry_obj = Entry(start=datetime.now(), end=datetime.now() + timedelta(days=1), repeat="daily", repeat_until=(datetime.now() + timedelta(days=30)).date(), content=unpublished_content)
        entry_obj.save()
        entry_obj.calendars.add(published_cal)
        entry_obj.save()
        queryset = EntryItem.permitted.all()
        self.failIf(queryset.count())
        Entry.objects.all().delete()
        
        # entries with staging calendars and content should be available in queryset but only if settings.STAGING = True
        # create staging cal and content entries
        entry_obj = Entry(start=datetime.now(), end=datetime.now() + timedelta(days=1), repeat="daily", repeat_until=(datetime.now() + timedelta(days=30)).date(), content=staging_content)
        entry_obj.save()
        entry_obj.calendars.add(staging_cal)
        entry_obj.save()
        settings.STAGING = False
        queryset = EntryItem.permitted.all()
        self.failIf(queryset.count())
        settings.STAGING = True
        queryset = EntryItem.permitted.all()
        self.failUnless(queryset.count())
        Entry.objects.all().delete()
        
        # entries with published cal and content should be available in queryset
        # create published cal and content entries
        entry_obj = Entry(start=datetime.now(), end=datetime.now() + timedelta(days=1), repeat="daily", repeat_until=(datetime.now() + timedelta(days=30)).date(), content=published_content)
        entry_obj.save()
        entry_obj.calendars.add(published_cal)
        entry_obj.save()
        queryset = EntryItem.permitted.all()
        self.failUnless(queryset.count())
        Entry.objects.all().delete()

        # queryset should not contain items for other sites
        mobile_site = Site(domain="mobi.address.com")
        mobile_site.save()
        # create published calendar for mobile site
        published_cal_mobile = Calendar(title='title', state='published')
        published_cal_mobile.save()
        published_cal_mobile.sites.add(mobile_site)
        published_cal_mobile.save()
        # create published calendar for mobile site
        published_content_mobile = ModelBase(title='title', state='published')
        published_content_mobile.save()
        published_content_mobile.sites.add(mobile_site)
        published_content_mobile.save()
        entry_obj = Entry(start=datetime.now(), end=datetime.now() + timedelta(days=1), repeat="daily", repeat_until=(datetime.now() + timedelta(days=30)).date(), content=published_content_mobile)
        entry_obj.save()
        entry_obj.calendars.add(published_cal_mobile)
        entry_obj.save()
        queryset = EntryItem.permitted.all()
        self.failIf(queryset.count())

    def test_by_model(self):
        # create published calendar
        published_cal = Calendar(title='title', state='published')
        published_cal.save()
        published_cal.sites.add(self.web_site)
        published_cal.save()
        
        # create published wanted content
        wanted_content = WantedContent(title='title', state='published')
        wanted_content.save()
        wanted_content.sites.add(self.web_site)
        wanted_content.save()
        
        # create published unwanted content
        unwanted_content = UnwantedContent(title='title', state='published')
        unwanted_content.save()
        unwanted_content.sites.add(self.web_site)
        unwanted_content.save()
        
        # create entries for wanted
        entry_obj = Entry(start=datetime.now(), end=datetime.now() + timedelta(days=1), repeat="daily", repeat_until=(datetime.now() + timedelta(days=30)).date(), content=wanted_content)
        entry_obj.save()
        entry_obj.calendars.add(published_cal)
        entry_obj.save()
        
        # create entries for unwanted
        entry_obj = Entry(start=datetime.now(), end=datetime.now() + timedelta(days=1), repeat="daily", repeat_until=(datetime.now() + timedelta(days=30)).date(), content=unwanted_content)
        entry_obj.save()
        entry_obj.calendars.add(published_cal)
        entry_obj.save()

        # should only return entry items for content of the provided model.
        queryset = EntryItem.permitted.by_model(WantedContent)
        for obj in queryset:
            self.failUnlessEqual(obj.content.class_name, 'WantedContent')
    
    def test_now(self):
        # create published calendar
        published_cal = Calendar(title='title', state='published')
        published_cal.save()
        published_cal.sites.add(self.web_site)
        published_cal.save()
        
        # create published content
        content = ModelBase(title='title', state='published')
        content.save()
        content.sites.add(self.web_site)
        content.save()
        
        # create entries
        entry_obj = Entry(start=datetime.now(), end=datetime.now() + timedelta(days=1), repeat="daily", repeat_until=(datetime.now() + timedelta(days=30)).date(), content=content)
        entry_obj.save()
        entry_obj.calendars.add(published_cal)
        entry_obj.save()

        # should return currently active entry items, ordered by start
        queryset = EntryItem.permitted.now()
        self.failUnless(queryset.count())
        for entry_item in queryset:
            self.failUnless(entry_item.start < datetime.now())
            self.failUnless(entry_item.end > datetime.now())

    def test_by_range(self):
        # create published calendar
        published_cal = Calendar(title='title', state='published')
        published_cal.save()
        published_cal.sites.add(self.web_site)
        published_cal.save()
        
        # create published content
        content = ModelBase(title='title', state='published')
        content.save()
        content.sites.add(self.web_site)
        content.save()
        
        start = datetime.now()
        end = start + timedelta(days=2)

        # create entryitem that spans the range
        spanning_entryitem = EntryItem(entry_id=1, start=start - timedelta(days=1), end=end + timedelta(days=1), content=content)
        spanning_entryitem.save()
        spanning_entryitem.calendars.add(published_cal)
        
        # create entryitem that precedes the range
        preceding_entryitem = EntryItem(entry_id=1, start=start - timedelta(days=1), end=start, content=content)
        preceding_entryitem.save()
        preceding_entryitem.calendars.add(published_cal)
        
        # create entryitem that procedes the range
        proceding_entryitem = EntryItem(entry_id=1, start=end, end=end + timedelta(days=1), content=content)
        proceding_entryitem.save()
        proceding_entryitem.calendars.add(published_cal)
        
        # create entryitem that is contained in the range
        contained_entryitem = EntryItem(entry_id=1, start=start, end=end, content=content)
        contained_entryitem.save()
        contained_entryitem.calendars.add(published_cal)
        
        # create entryitem that starts before range but ends within range
        end_contained_entryitem = EntryItem(entry_id=1, start=start-timedelta(days=1), end=end, content=content)
        end_contained_entryitem.save()
        end_contained_entryitem.calendars.add(published_cal)
        
        # create entryitem that starts in range but ends after range
        start_contained_entryitem = EntryItem(entry_id=1, start=start, end=end+timedelta(days=1), content=content)
        start_contained_entryitem.save()
        start_contained_entryitem.calendars.add(published_cal)
        
        result = EntryItem.permitted.by_range(start, end)

        # spanning entry should be in result
        self.failUnless(spanning_entryitem in result)

        # preceding entry should not be in result
        self.failIf(preceding_entryitem in result)
        
        # proceding entry should not be in result
        self.failIf(proceding_entryitem in result)

        # contained entryitem should be in result
        self.failUnless(contained_entryitem in result)
        
        # entry starting before range but ending withing range should be in result
        self.failUnless(end_contained_entryitem in result)
        
        # entry starting in range but ending after range should be in result
        self.failUnless(start_contained_entryitem in result)
    
    def test_by_date(self):
        # create published calendar
        published_cal = Calendar(title='title', state='published')
        published_cal.save()
        published_cal.sites.add(self.web_site)
        published_cal.save()
        
        # create published content
        content = ModelBase(title='title', state='published')
        content.save()
        content.sites.add(self.web_site)
        content.save()
        
        # create entries
        entry_obj = Entry(start=datetime.now(), end=datetime.now() + timedelta(days=1), repeat="daily", repeat_until=(datetime.now() + timedelta(days=30)).date(), content=content)
        entry_obj.save()
        entry_obj.calendars.add(published_cal)
        entry_obj.save()
        
        now = datetime.now()
        date = now.date()
       
        # result should only contain the entry for the date
        result = EntryItem.permitted.by_date(date)
        self.failUnlessEqual(result.count(), 1)
