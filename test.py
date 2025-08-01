import datetime

a =datetime.datetime.now()
current_datetime_without_ms = a.strftime("%Y-%m-%d %H:%M:%S")
print(current_datetime_without_ms)