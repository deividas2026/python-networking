from datetime import datetime

def printt(message):
    now = datetime.now()
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
    print(formatted_time, message) 

