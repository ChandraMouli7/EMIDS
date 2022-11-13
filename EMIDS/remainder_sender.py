import datetime
from twilio.rest import Client

class Date:
    def __init__(self, d, m, y):
        self.d = d
        self.m = m
        self.y = y

monthDays = [31, 28, 31, 30, 31, 30,
             31, 31, 30, 31, 30, 31]
 
def countLeapYears(d):
 
    years = d.y

    if (d.m <= 2):
        years -= 1

    return int(years / 4) - int(years / 100) + int(years / 400)
 
def getDifference(dt1, dt2):
 
    n1 = dt1.y * 365 + dt1.d

    for i in range(0, dt1.m - 1):
        n1 += monthDays[i]

    n1 += countLeapYears(dt1)

 
    n2 = dt2.y * 365 + dt2.d
    for i in range(0, dt2.m - 1):
        n2 += monthDays[i]
    n2 += countLeapYears(dt2)

    return (n2 - n1)

def send_reminder(patient_id, s_date):
    c_date = datetime.datetime.now()
    c_month = int(c_date.strftime("%m"))
    c_day = int(c_date.strftime("%d"))
    c_year = int(c_date.strftime("%Y"))
    current_date = Date(c_day, c_month, c_year)
    s_month = int(s_date.strftime("%m"))
    s_day = int(s_date.strftime("%d"))
    s_year = int(s_date.strftime("%Y"))
    scheduled_date = Date(s_day, s_month, s_year)
    difference = getDifference(current_date, scheduled_date)
    if difference<=2 and difference>0:
        send_message(s_date)

    
def send_message(s_date):
    account_sid = 'ACc5eb134a0871670568c1adbf7c756ebb'
    auth_token = '85c52de88fc3f7e2b66a1e42d62ca95b'
    client = Client(account_sid, auth_token)
    date_time = s_date.strftime("%m-%d-%Y")
    message = client.messages \
                    .create(
                         body="You have an appointment on "+date_time,
                         from_='+15627845649',
                         to='+919940485632'
                     )
