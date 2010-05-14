from datetime import datetime, timedelta

from django.db import models

from content.models import ModelBase

def save_handler_does_not_repeat(entry):
    # raise an error if wrong handler is triggered
    if entry.repeat != 'does_not_repeat':
        raise Exception("In handler 'save_handler_does_not_repeat' for entry with repeat set as '%s'" % entry.repeat)

    # delete all entry items related to this entry
    # XXX: yes this is not super efficient, but results in the cleanest code.
    EntryItem.objects.filter(entry=entry).delete()

    # create a single entryitem linked to entry with provided entry's fields
    entry_item = EntryItem(start=entry.start, end=entry.end, entry=entry, content=entry.content)
    entry_item.save()

    for calendar in entry.calendars.all():
        entry_item.calendars.add(calendar)

def save_handler_daily(entry):
    # raise an error if wrong handler is triggered
    if entry.repeat != 'daily':
        raise Exception("In handler 'daily' for entry with repeat set as '%s'" % entry.repeat)
   
    # check for repeat until:
    if not entry.repeat_until:
        raise Exception("Entry should provide repeat_until value for 'daily' repeat.")

    # delete all entry items related to this entry
    # XXX: yes this is not super efficient, but results in the cleanest code.
    EntryItem.objects.filter(entry=entry).delete()

    # create entryitem linked to entry for each day until entry's repeat until value.
    day = entry.start.date()
    duration = entry.end - entry.start
    while day < entry.repeat_until:
        start = entry.start
        start = start.replace(year=day.year, month=day.month, day=day.day)
        end = start + duration
        entry_item = EntryItem(start=start, end=end, entry=entry, content=entry.content)
        entry_item.save()

        for calendar in entry.calendars.all():
            entry_item.calendars.add(calendar)

        day = day + timedelta(days=1)
    
class Calendar(ModelBase):
    class Meta():
        verbose_name = "Calendar"
        verbose_name_plural = "Calendars"

class EntryAbstract(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    content = models.ForeignKey(
        'content.ModelBase',
    )
    class Meta():
        abstract = True

class Entry(EntryAbstract):
    repeat = models.CharField(
        max_length=64,
        choices=(
            ('does_not_repeat', 'Does Not Repeat'),
            ('daily', 'Daily'), 
            ('weekly', 'Weekly'), 
            ('monthly', 'Monthly'), 
            ('yearly', 'Yearly'),
        ),
        default='Does Not Repeat',
    )
    repeat_until = models.DateField(
        blank=True,
        null=True,
    )
    calendars = models.ManyToManyField(
        'cal.Calendar',
        related_name='entry_calendar'
    )

    def save(self, *args, **kwargs):
        super(Entry, self).save(*args, **kwargs)
        # create new entry items based on repeat setting
        repeat_handlers = {
            'does_not_repeat': save_handler_does_not_repeat,
            'daily': save_handler_daily,
        }
        repeat_handlers[self.repeat](self)

    def __unicode__(self):
        return "Entry for %s" % self.content.title

    class Meta():
        verbose_name = "Entry"
        verbose_name_plural = "Entries"

class EntryItem(EntryAbstract):
    entry = models.ForeignKey(
        'cal.Entry',
    )
    calendars = models.ManyToManyField(
        'cal.Calendar',
        related_name='entryitem_calendar'
    )
