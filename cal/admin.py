from django.contrib import admin

from cal.models import Calendar, Entry
from content.admin import ModelBaseAdmin

admin.site.register(Calendar, ModelBaseAdmin)
admin.site.register(Entry)
