from datetime import datetime, timedelta

# TODO should be done on client side for live updates. but the logic is here.

def format_datetime(datetime_obj, full=False):
    full_str = datetime_obj.strftime('%-d %B %Y at %H:%M')
    if full:
        return full_str
    now = datetime.now()
    if datetime_obj > (now - timedelta(minutes=1)):
        return f'just now'
    elif datetime_obj > (now - timedelta(hours=1)):
        minutes = int((now - datetime_obj).total_seconds() / 60)
        return f'{minutes} minute{"s" if minutes > 1 else ""} ago'
    elif datetime_obj > (now - timedelta(hours=24)):
        hours = int((now - datetime_obj).total_seconds() / 3600)
        return f'{hours} hour{"s" if hours > 1 else ""} ago'
    elif datetime_obj > (now - timedelta(hours=48)):
        return f'yesterday'
    else:
        return full_str