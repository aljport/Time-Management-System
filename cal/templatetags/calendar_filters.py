from django import template

register = template.Library()

@register.filter
def modulo(num, val):
    return num % val

@register.filter
def find_events_date(all_events,day_date):
    return all_events.filter(start_time__day=day_date)