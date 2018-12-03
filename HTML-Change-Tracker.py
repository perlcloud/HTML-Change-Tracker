import os
import time
import random
import urllib.request
from datetime import  datetime
from bs4 import BeautifulSoup

def create_log():
    # Create log and file folder
    target_name = 'Denim Overalls'.replace(' ','-')
    script_path = os.path.dirname(os.path.realpath(__file__))
    global log_path
    log_path = script_path + '\\' + target_name
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    # Start log
    log_file_name = 'log_' + str(target_name) + '.csv'
    global log_file_path
    log_file_path = log_path + '\\' + log_file_name
    if not os.path.isfile(log_file_path):
        global log
        log = open(log_file_path,'w+')
        log.write('Loop Count' + ',' + 'Timestamp' + ',' + 'Note\n')
        log.close

def get_html():
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
    global url
    url = 'https://www.zara.com/us/en/lined-denim-overalls-p05854594.html'
    headers={'User-Agent':user_agent,} 
    request=urllib.request.Request(url,None,headers)
    response = urllib.request.urlopen(request)
    global html_data
    html_data = BeautifulSoup(response.read())

def get_old_html():
    get_html()
    global old_html_target
    old_html_target = str(html_data.find_all("div", class_="size-list"))
    html_state_file_name = log_path + '\\' + 'html_state_' + str(datetime.now()).replace(':','-') + '.html'
    html_state_file = open(html_state_file_name,'w+')
    html_state_file.write(str(html_data))

def get_new_html():
    get_html()
    global new_html_target
    new_html_target = str(html_data.find_all('div', class_='size-list'))

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

# Start log
create_log()
start_time = datetime.now()
loop_count = 0
log = open(log_file_path,'a')
log.write(' ' + ',' + str(datetime.now()) + ',' + 'Start Time\n')
log.flush()

# Get current html state
get_old_html()
size_list_change = True

while (size_list_change == True):
    loop_count = loop_count + 1
    get_new_html()

    if(str(old_html_target) == str(new_html_target)):
        print(str(loop_count) + '   ' + str(datetime.now()) + '  HTML Target Unchanged')
        log.write(str(loop_count) + ',' + str(datetime.now()) + ',' + 'HTML Target Unchanged\n')
        log.flush()
        time.sleep(sleep_time())
    else:
        send_email('HTML Target Changed!!?', str(url) + ' Loop: ' + str(loop_count))
        log.write(str(loop_count) + ',' + str(datetime.now()) + ',' + 'HTML Target Changed\n')
        end_time = datetime.now()
        log.write(' ' + ',' + str(end_time) + ',' + 'End Time\n')
        log.close
        print(str(loop_count) + '   ' + str(datetime.now()) + '  HTML Target Changed')
        get_old_html() # Start again

