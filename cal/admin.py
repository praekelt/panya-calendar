from django.contrib import admin

from cal.models import Calendar, Entry
from panya.admin import ModelBaseAdmin

class EntryAdmin(admin.ModelAdmin):
    list_display = ('content', 'start', 'end', 'repeat', 'repeat_until')
    list_filter = ('repeat',)
    search_fields = ('content__title', 'content__description')

admin.site.register(Calendar, ModelBaseAdmin)
admin.site.register(Entry, EntryAdmin)
