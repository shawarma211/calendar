from datetime import datetime, timedelta
from calendar import monthrange

def calendar(months):
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    month = today.month - 1 + months
    year = today.year + month // 12
    
    month = month % 12 + 1
    day = min(today.day, monthrange(year, month)[1])
    date = datetime(year, month, day)

    month_days=[]
    first_day = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_day = first_day

    while last_day.month == first_day.month:
        last_day += timedelta(days=1)
    
    first_day -= timedelta(days=first_day.weekday())
    last_day += timedelta(days=7 - last_day.weekday())

    week = -1
    while first_day != last_day:
            if first_day.weekday() == 0:
                month_days.append([])
                week+=1
            month_days[week].append(first_day)
            first_day += timedelta(days=1)
    
    return month_days