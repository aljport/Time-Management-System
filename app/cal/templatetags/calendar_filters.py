import pytz
from django.utils import timezone
from django import template
from datetime import datetime, timedelta
from django.db.models import F

from collections import defaultdict


register = template.Library()

@register.filter
def modulo(num, val):
    return num % val

@register.filter
def find_events_date(all_events,day_date):
    return all_events.filter(start_time__day=day_date)


@register.filter
def find_ongoing_event(all_events, day_date):
    my_date = int(day_date)
    return all_events.filter(start_time__date__day__lte=my_date, end_time__date__day__gte=my_date)


@register.filter
def find_ongoing_week_event(all_events, day_date):
    ongoing_events = []
    
    est = pytz.timezone('US/Eastern')

    # Convert the time to the desired timezone (EST)
    start_time_est = event.start_time.astimezone(est)

    # Convert `day_date` and `day_hour` into a single datetime object for comparison
    #target_datetime = datetime.combine(day_date)

    for event in all_events:
        # Check if the event is ongoing at `target_datetime`
        if start_time_est.start_time.day <= day_date <= start_time_est.end_time.day:
            ongoing_events.append(event)
    
    return ongoing_events

@register.filter
def find_ongoing_long_event(all_events, day_date):
    my_date = int(day_date)
    return all_events.filter(start_time__date__day__lte=my_date, end_time__date__day__gte=my_date).exclude(end_time__lte=F('start_time') + timedelta(hours=24))

@register.filter
def find_ongoing_day_event(all_events, day_date):
    my_date = int(day_date)
    return all_events.filter(start_time__date__day__lte=my_date, end_time__date__day__gte=my_date).exclude(end_time__gt=F('start_time') + timedelta(hours=24))

@register.filter
def calculate_top_value(event, current_date):

    est = pytz.timezone('US/Eastern')

    # Convert the time to the desired timezone (EST)
    start_time_est = event.start_time.astimezone(est)

    # Get the hour and minute in EST
    hour = start_time_est.hour
    minute = start_time_est.minute
    day = start_time_est.day

    #hour = event.start_time.hour
    #minute = event.start_time.minute
    top = 0
    if(current_date > day):
        top = 0
    else:

        top = (hour * 7.5) + (minute * 0.125)

    return f"{top}vh"


@register.filter
def calculate_bottom_value(event, current_date):

    est = pytz.timezone('US/Eastern')

    # Convert the time to the desired timezone (EST)
    end_time_est = event.end_time.astimezone(est)

    # Get the hour and minute in EST
    hour = end_time_est.hour
    minute = end_time_est.minute
    day = end_time_est.day

    bottom = 0
    if(current_date < day):
        bottom = -97.5
    else:
    #-97.5 is bottom
    #hour = event.start_time.hour
    #minute = event.start_time.minute
        bottom = 82.5 - ((hour * 7.5) + (minute * 0.125))

    return f"{bottom}vh"


@register.filter
def calculate_long_left_value(event, start_date):

    est = pytz.timezone('US/Eastern')

    # Convert the time to the desired timezone (EST)
    start_time_est = event.start_time.astimezone(est)
    start_date_est = start_date.astimezone(est)

    # Get the hour and minute in EST
    day = start_time_est.day

    start_day = start_date_est.day

    left = 0
    if(start_day > day):
        left = 0
    else:
        left = (day-start_day) * 10.5
    
    left = (left / 73.5) * 100

    return f"{left}%"


@register.filter
def calculate_long_right_value(event, end_date):

    est = pytz.timezone('US/Eastern')

    # Convert the time to the desired timezone (EST)
    end_time_est = event.end_time.astimezone(est)
    end_date_est = end_date.astimezone(est)

    # Get the hour and minute in EST
    hour = end_time_est.hour
    minute = end_time_est.minute
    day = end_time_est.day

    end_day = end_date_est.day
    end_day = end_day - 1

    right = 0
    if(end_day < day):
        right = 0
    else:
    #73.5 is right
    #hour = event.start_time.hour
    #minute = event.start_time.minute
        right = ((end_day - day) * 10.5)

    right = (right / 73.5) * 100

    return f"{right}%"

@register.filter
def calculate_est_begin(event):

    est = pytz.timezone('US/Eastern')

    # Convert the time to the desired timezone (EST)
    start_time_est = event.start_time.astimezone(est)

    # Get the hour and minute in EST
    hour = start_time_est.hour
    minute = start_time_est.minute

    #hour = event.start_time.hour
    #minute = event.start_time.minute
    #top = (hour * 7.5) + (minute * 0.125)\
    top = (hour * 7.5) + (minute * 0.125)

    return f"Hour : {hour}, minute : {minute}, top: {top}"

@register.filter
def calculate_est_end(event, current_date):

    est = pytz.timezone('US/Eastern')

    # Convert the time to the desired timezone (EST)
    end_time_est = event.end_time.astimezone(est)

    # Get the hour and minute in EST
    hour = end_time_est.hour
    minute = end_time_est.minute

    #hour = event.start_time.hour
    #minute = event.start_time.minute
    #top = (hour * 7.5) + (minute * 0.125)
    day = end_time_est.day
    
    
    if(current_date < day):
        bottom = -97.5
    else:
    #hour = event.start_time.hour
    #minute = event.start_time.minute
        bottom = 82.5 - ((hour * 7.5) + (minute * 0.125))

    return f"Hour : {hour}, minute : {minute}, bottom: {bottom}"


@register.filter
def calculate_events(event):

    est = pytz.timezone('US/Eastern')

    # Convert the time to the desired timezone (EST)
    start_time_est = event.start_time.astimezone(est)

    # Get the hour and minute in EST
    hour = start_time_est.hour
    minute = start_time_est.minute

    #hour = event.start_time.hour
    #minute = event.start_time.minute
    top = (hour * 7.5) + (minute * 0.125)

    return f"{top}vh"


@register.simple_tag
def calculate_offset(events, current_date):

    est = pytz.timezone('US/Eastern')

    # Convert the time to the desired timezone (EST)
    #end_time_est = event.end_time.astimezone(est)
    #end_date_est = end_date.astimezone(est)

    # Get the hour and minute in EST
    day_events = [e for e in events if (int(e.start_time.astimezone(est).day) <= int(current_date) and int(e.end_time.astimezone(est).day) >= int(current_date))]
    # Sort events by start time
    day_events.sort(key=lambda x: x.start_time.astimezone(est))

    # Data structures
    time_blocks = defaultdict(list)  # Tracks events for each hour block
    position_map = defaultdict(set)  # Tracks occupied positions for each hour block
    results = []

    # Step 1: Populate time blocks and assign positions
    for event in day_events:
        start = event.start_time.astimezone(est).hour
        end = event.end_time.astimezone(est).hour

        # Calculate overlap and determine position
        max_overlap = 0
        assigned_position = None

        for hour in range(start, end + 1):
            max_overlap = max(max_overlap, len(time_blocks[hour]))
            # Check for the first available position
            for pos in range(1, max_overlap + 2):  # Allow room for a new position
                if pos not in position_map[hour]:
                    assigned_position = pos
                    break

        # Assign the determined position to all affected hours
        for hour in range(start, end + 1):
            time_blocks[hour].append(event)
            position_map[hour].add(assigned_position)

        # Append the result as "max-pos-event_id"
        results.append(f"week-event-{max_overlap + 1}-{assigned_position}")

    return results


#Currently doesn't account for if two events have the same starting hour
#
@register.simple_tag
def calculate_offsets(events, current_date):

    est = pytz.timezone('US/Eastern')

    class event_struct:
        def __init__(self, event, index):
            self.index = index
            self.event = event

    class gap_struct:
        def __init__(self, hour, event_list, start, end, max):
            self.hour = hour
            self.event_list = event_list
            self.top_gap = start
            self.bottom_gap = end
            self.max = max


    class new_gap_struct:
        def __init__(self, event_list, start, length, max):
            self.event_list = event_list
            self.start = start
            self.length = length
            self.max = max

    class EventTemplateModel:
        def __init__(self, event):
            self.title = event.title
            self.description = event.description
            # maybe do math to split these values up?
            self.start_time = event.start_time.astimezone(est)
            self.end_time = event.end_time.astimezone(est)
            self.event_start_day = 0
            self.event_start_hour = 0
            self.event_start_min = 0

            self.event_end_day = 0
            self.event_end_hour = 0
            self.event_end_min = 0

            self.user_created = event.user_created
            self.id = event.id
            self.attendee = event.attendee
            self.location = event.location
            self.max = 0
            self.pos = 0
            self.width = 0
            self.hour_list = []

        
    eventList = []
    
    #get all events of current day and store it
    for event in events:
        new_event = EventTemplateModel(event)

        #if event doesn't start on that day, sets the temp date to be midnight
        if(new_event.start_time.day < current_date):
            new_event.event_start_day = current_date
            new_event.event_start_hour = 0
            new_event.event_start_min = 0
        else:
            new_event.event_start_day = event.start_time.astimezone(est).day
            new_event.event_start_hour = new_event.start_time.hour
            new_event.event_start_min = new_event.start_time.minute

        #if event doesn't start on that day, sets the temp date to be midnight of next day
        if(new_event.end_time.day > current_date):
            new_event.event_end_day = current_date
            new_event.event_end_hour = 23
            new_event.event_end_min = 59
        else:
            new_event.event_end_day = new_event.end_time.day
            new_event.event_end_hour = new_event.end_time.hour
            new_event.event_end_min = new_event.end_time.minute

        for hour in range(new_event.event_start_hour, new_event.event_end_hour + 1):
            new_event.hour_list.append(int(hour))

        eventList.append(new_event)

    listLength = len(eventList)

    # sort list by start date
    eventList.sort(key=lambda x: x.event_start_hour, reverse=False)

    gap_list = {}
    max_hour_list = {}
    length = 0

    i = 0
    hour_map ={}
    temp_gap_list = []
    while i < 24:

        # need dictionary since we need to keep track of index of events from eventList
        my_hour_event_list = []

        start = True
        end = True

        # add each event for each hour here
        index = 0
        for event in eventList:
            #print("current event: ", event.title)
            if i in event.hour_list:
                if event.event_start_hour < i:
                    start = False
                if event.event_end_hour > i:
                    end = False

                # pairs the event and index together for easier reference later
                new_event_struct = event_struct(event, index)
                my_hour_event_list.append(new_event_struct)

            index += 1

        length = len(my_hour_event_list)
        # assign max and pos here
        hour_map[i] = length
        new_gap = gap_struct(i, my_hour_event_list, start, end, length)
        temp_gap_list.append(new_gap)
        i += 1

    gap_list = []
    i = 0
    # combine holes here
    # unfinished
    #print("\nCombining Holes\n")
    tracker = 1
    while i < 24:
        tracker = 1
        current_gap = temp_gap_list[i]

        start_time = current_gap.hour
        current_max = current_gap.max
        big_max = current_max

        # code for if there is no next gap
        if i + 1 >= len(temp_gap_list):
            new_gap = new_gap_struct(current_gap.event_list, start_time, 1, current_max)
            gap_list.append(new_gap)
            break

        next_gap = temp_gap_list[i + 1]

        # list of list
        new_list = []

        running = True
        while running:
            if current_gap.bottom_gap and current_gap.top_gap:
                break
            if current_gap.bottom_gap and next_gap.top_gap:
                new_gap = new_gap_struct(new_list, start_time, tracker, big_max)
                gap_list.append(new_gap)
                running = False
                break

            if current_gap == next_gap:

                new_gap = new_gap_struct(new_list, start_time, tracker, big_max)
                gap_list.append(new_gap)
                running = False
                break

            if current_max > big_max:
                big_max = current_max

            new_list.append(current_gap.event_list)

            
            tracker += 1
            if tracker >= 24:
                break

            current_gap = next_gap
            current_max = current_gap.max

            if tracker + i >= 24:
                new_gap = new_gap_struct(new_list, start_time, tracker, big_max)
                gap_list.append(new_gap)
                running = False
                break
            next_gap = temp_gap_list[tracker + i]
            

            

        i += tracker

    # sets sizes for gaps
    for gap in gap_list:

        max_size = gap.max

        for new_hour_list in gap.event_list:

            pos_taken = []
            for event in new_hour_list:
                event.event.max = max_size
                if event.event.pos != 0:
                    pos_taken.append(event.event.pos)

            pos_taken.sort()

            # loop through each event in hour_list
            pos_counter = 1
            pos_index = 0
            for event in new_hour_list:
                if len(pos_taken) > 0:

                    if len(pos_taken) == len(new_hour_list):

                        continue
                    elif event.event.pos > 0:
                        continue

                    else:
                        #pos_curr_index = pos_taken[pos_index]
                        for i in range(1, max_size + 1):

                            if i not in pos_taken:
                                event.event.pos = i
                                pos_taken.append(i)
                                pos_taken.sort()
                                break

                #Goes into this if the gap block is at the beginning
                else:
                    event.event.pos = pos_counter
                    current_event_id = event.event.id
                    
                    for the_event in gap.event_list:

                        for curr_event in the_event:

                            #identify the event here
                            if current_event_id == curr_event.event.id:
                                curr_event.event.pos = pos_counter

                    pos_counter += 1

    mod_event_list = []
    index_list = []
    for gap in gap_list:
        for event_list in gap.event_list:
            for event in event_list:
                if event.index not in index_list:
                    index_list.append(event.index)
                    mod_event_list.append(event)

    #update event_list now
    for new_event in mod_event_list:
       current_index = new_event.index
       current_event = new_event.event

       eventList[current_index].max = current_event.max
       eventList[current_index].pos = current_event.pos

    return eventList