from datetime import datetime, timedelta


def format_datetime(datetime_obj):
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
        return datetime_obj.strftime('%d/%m/%Y %H:%M')