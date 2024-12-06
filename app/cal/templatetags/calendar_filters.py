from django import template

register = template.Library()

@register.filter
def modulo(num, val):
    return num % val

@register.filter
def find_events_date(all_events,day_date):
    return all_events.filter(start_time__day=day_date)


@register.filter
def find_ongoing_event(all_events, day_date):
    my_date = str(day_date)
    return all_events.filter(start_time__date__lte=my_date, end_time__date__gte=my_date)

@register.filter
def count_events_on_day(all_events, day_date):
    return all_events.filter(start_time__date=day_date).count()
