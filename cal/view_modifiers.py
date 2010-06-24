import calendar
from datetime import datetime, timedelta

from panya.view_modifiers import ViewModifier
from panya.view_modifiers.items import GetItem

class EntryByWeekdayItem(GetItem):
    def __init__(self, request, title, get, date, default):
        self.date=date
        super(EntryByWeekdayItem, self).__init__(request=request, title=title, get=get, default=default)

    def modify(self, view):
        view.params['queryset'] = view.params['queryset'].by_date(self.date)
        return view

class EntriesByWeekdaysViewModifier(ViewModifier):
    def __init__(self, request, *args, **kwargs):
        self.items = []
        now = datetime.now().date()
        
        day_names = [name for name in calendar.day_abbr]
        current_day = day_names[now.weekday()]

        
        dates_by_day = {}
        date = now
        while date < now + timedelta(days=7):
            dates_by_day[day_names[date.weekday()]] = date
            date = date + timedelta(days=1)

        for name in day_names:
            self.items.append(EntryByWeekdayItem(
                request=request,
                title=name,
                get={'name': 'day', 'value': name},
                date=dates_by_day[name],
                default=current_day==name,
            ))
            
        super(EntriesByWeekdaysViewModifier, self).__init__(request)
