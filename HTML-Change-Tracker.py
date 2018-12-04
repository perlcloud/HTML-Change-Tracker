import os
import time
import json
import random
import smtplib
import urllib.request
from datetime import  datetime
from datetime import timedelta
from bs4 import BeautifulSoup

# Set Variables
script_path = os.path.dirname(os.path.realpath(__file__))
with open(script_path + '\\Tracking-Var-Data.json') as json_data: # Set Variables from json
    json_data = json.load(json_data)

    project_name = json_data['project_details'][0]['name'].replace(' ','-')
    url = json_data['project_details'][0]['url']
    target_name = json_data['project_details'][0]['target'][0]['name']
    target_class = json_data['project_details'][0]['target'][0]['class']
    user = json_data['notify'][0]['sender'][0]['user']
    pwd = json_data['notify'][0]['sender'][0]['pass']
    recipient = json_data['notify'][0]['recipient']

def create_log():               # Creates and starts log file
    # Create project folder
    global log_path
    log_path = script_path + '\\' + project_name
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    
    # Create log file
    log_file_name = 'log_' + str(project_name) + '.csv'
    global log_file_path
    log_file_path = log_path + '\\' + log_file_name
    if not os.path.isfile(log_file_path):
        global log
        log = open(log_file_path,'w+')
        log.write('Loop Count,Timestamp,Download Time,Note\n') # csv headers
        log.close

def get_html():                 # Downloads target html
    # Download timer start
    get_html_time_start = time.time()
    
    # Download HTML
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
    headers={'User-Agent':user_agent,}
    request = urllib.request.Request(url,None,headers)
    response = urllib.request.urlopen(request)
    global html_state
    html_state = BeautifulSoup(response.read(), 'html.parser')
    global html_target
    html_target = str(html_state.find_all(target_name, class_=target_class))
    
    # Download timer end & calc
    get_html_time_end = time.time()
    global get_html_time
    get_html_time = get_html_time_start - get_html_time_end

def get_old_html():             # Load original html state and back up
    get_html()

    # Make backup of current html state
    html_state_file_name = log_path + '\\' + 'html_state_' + str(datetime.now()).replace(':','-') + '.html'
    with open(html_state_file_name,'w+') as html_state_file:
        html_state_file.write(str(html_state))
    
    global old_html
    old_html = html_target

def get_new_html():             # Load a current copy of the html target
    get_html()
    global new_html
    new_html = html_target

def send_email(subject, body):  # Send notification via gmail account
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
        log = open(log_file_path,'a')
        log.write(' ' + ',' + str(datetime.now()) + ',' + ' ,' + 'Email Notification Sent\n')
        log.flush()
        print('Email Notification Sent')
    except:
        log = open(log_file_path,'a')
        log.write(' ' + ',' + str(datetime.now()) + ',' + ' ,' + 'Email Notification Failed\n')
        log.flush()
        print('Email Notification Failed')

def sleep_time():               # Randomize breaks between loops
    return random.randint(60,181)

# Start log
create_log()
loop_count = 0
start_time = datetime.now()
log = open(log_file_path,'a')
log.write(' ' + ',' + str(datetime.now()) + ',' + ' ,' + 'Start Time\n')
log.flush()

# Get current html state
get_old_html()
# size_list_change = True

while True:
    loop_count = loop_count + 1
    get_new_html()

    if(old_html == new_html):
        print(str(loop_count) + '   ' + str(datetime.now()) + '   ' + str(get_html_time) + '    ' + 'HTML Target Unchanged')
        log.write(str(loop_count) + ',' + str(datetime.now()) + ',' + str(get_html_time) + ',' + 'HTML Target Unchanged\n')
        log.flush()
        time.sleep(sleep_time())
    else:
        send_email('HTML Target Changed!!?', str(url) + ' Loop: ' + str(loop_count))
        log.write(str(loop_count) + ',' + str(datetime.now()) + ',' + str(get_html_time) + ',' + 'HTML Target Changed\n')
        end_time = datetime.now()
        log.write(' ' + ',' + str(end_time) + ',' + ' ,' + 'End Time\n')
        log.close
        print(str(loop_count) + '   ' + str(datetime.now()) + '  HTML Target Changed')
        get_old_html() # Start again
        loop_count = 0

