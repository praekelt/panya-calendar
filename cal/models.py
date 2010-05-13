from django.db import models

from content.models import ModelBase

def save_handler_does_not_repeat(entry):
    # raise an error if wrong handler is triggered
    if entry.repeat != 'does_not_repeat':
        raise Exception("In handler 'save_handler_does_not_repeat' for entry with repeat set as '%s'" % entry.repeat)
    
def save_handler_daily(entry):
    # raise an error if wrong handler is triggered
    if entry.repeat != 'daily':
        raise Exception("In handler 'daily' for entry with repeat set as '%s'" % entry.repeat)
    
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
    calendar = models.ManyToManyField(
        'cal.Calendar',
        related_name='entry_calendar'
    )

    def save(self, *args, **kwargs):
        repeat_handlers = {
            'does_not_repeat': save_handler_does_not_repeat,
            'daily': save_handler_daily,
        }
        repeat_handlers[self.repeat](self)
        super(Entry, self).save(*args, **kwargs)

    def __unicode__(self):
        return "Entry for %s" % self.content.title

    class Meta():
        verbose_name = "Entry"
        verbose_name_plural = "Entries"

class EntryItem(EntryAbstract):
    entry = models.ForeignKey(
        'cal.Entry',
    )
    calendar = models.ManyToManyField(
        'cal.Calendar',
        related_name='entryitem_calendar'
    )
