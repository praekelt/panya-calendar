from django.db import models

from content.models import ModelBase

class Calendar(ModelBase):
    pass

class EntryAbstract(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    calendar = models.ManyToMany(
        'calendar.Calendar')
    )
    content = models.ForeignKey(
        'content.ModelBase'
    )
    class Meta():
        abstract = True

class Entry(EntryAbstract):
    repeat = models.CharField(
        max_length=64
        choices=(
            (None, 'Does Not Repeat')
            ('daily', 'Daily'), 
            ('weekly', 'Weekly'), 
            ('monthly', 'Monthly'), 
            ('yearly', 'Yearly'),
        ),
        blank=True,
        null=True,
    )
    repeat_until = models.DateField(
        blank=True,
        null=True,
    )

class EntryItem(EntryAbstract):
    entry = models.ForeignKey(
        'calendar.Entry',
    )
