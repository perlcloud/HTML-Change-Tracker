import os
import time
import random
import urllib.request
from datetime import  datetime
from bs4 import BeautifulSoup

target_name = 'Denim Overalls'
target_name = target_name.replace(' ','_')

def get_html():
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
    global url
    url = 'https://www.zara.com/us/en/lined-denim-overalls-p05854594.html'
    headers={'User-Agent':user_agent,} 
    request=urllib.request.Request(url,None,headers)
    response = urllib.request.urlopen(request)
    global html_data
<<<<<<< HEAD
    html_data = BeautifulSoup.prettify(response.read())
=======
    html_data = BeautifulSoup(response.read())
>>>>>>> 95ef8baf716f8ed0342791dabb95b60f291dd7b3

def get_old_size_list():
    get_html()
    global old_size_list
    old_size_list = str(html_data.find_all("div", class_="size-list"))

def get_new_size_list():
    get_html()
    global new_size_list
    new_size_list = str(html_data.find_all('div', class_='size-list'))

def send_email(subject, body):
    import smtplib

    user = input('Whats your email? ')                     # Enter your gmail
    pwd = input('Whats your password? ')                   # Enter your password
    recipient = ['phone@txt.att.net', 'phone@txt.att.net']  # Replace recipient's with emails or phone numbers 
    # subject = 'Auto Notification From: ' + os.path.basename(__file__)

    FROM = user
    TO = recipient if isinstance(recipient, list) else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = '''From: %s\nTo: %s\nSubject: %s\n\n%s
    ''' % (FROM, ', '.join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(user, pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print('successfully sent the mail')
    except:
        print('failed to send mail')

def sleep_time():
    return random.randint(60,181)


# Keep track of time and loops in log
start_time = datetime.now()
loop_count = 0
my_path = os.path.dirname(os.path.realpath(__file__))
log_file_name = 'log_' + str(datetime.now()).replace(':','-') + '.txt'
log_file = my_path+'\\'+log_file_name
print(log_file)
log = open(log_file,'w+')
log.write('Start Time: ' + str(start_time) + '\n')
log.close

# Start of script 
get_old_size_list()
size_list_change = True

while (size_list_change == True):
    loop_count = loop_count + 1
    get_new_size_list()

    if(str(old_size_list) == str(new_size_list)):
        print(str(loop_count) + '   ' + str(datetime.now()) + '  Inventory Unchanged')
        log = open(log_file,'a')
        log.write(str(loop_count) + '   ' + str(datetime.now()) + '  Inventory Unchanged\n')
        time.sleep(sleep_time())
    else:
        send_email('Inventory Changed!!?', str(url) + ' Loop: ' + str(loop_count))
        log = open(log_file,'a')
        log.write(str(loop_count) + '   ' + str(datetime.now()) + '  Inventory Changed\n')
        end_time = datetime.now()
        log.write('End Time: ' + str(end_time) + '\n')
        log.close
        print(str(loop_count) + '   ' + str(datetime.now()) + '  Inventory Changed')
        get_old_size_list() # Start again

