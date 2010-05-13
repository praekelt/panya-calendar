from django.contrib import admin

from calendar.models import Calendar, Entry
from content.admin import ModelAdmin

admin.site.register(Calendar, ModelAdmin)
admin.site.register(Entry)
