import os
import re
import csv
import yaml
import time
import pickle
import random
import smtplib

import getHTML

from datetime import datetime


def csv_write(record):
    """Helper function to load data into the csv"""
    with open(log_file_path, "a", newline="") as log:
        file_writer = csv.writer(
            log,
            delimiter=",",
            quotechar='"',
            quoting=csv.QUOTE_ALL,
        )
        file_writer.writerow(record)


def log(event, loop_count="", download_time=""):
    """Logs events to the terminal and CSV"""
    log_data = [
        str(run_count),
        str(loop_count),
        str(datetime.now()),
        event,
        str(download_time),
    ]

    # Create .csv if one does not exist
    if not os.path.isfile(log_file_path):
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        # Add headers
        csv_write(
            [
                "Run Count",
                "Loop Count",
                "Timestamp",
                "Event",
                "Download Time",
            ]
        )
    # Log event
    try:
        csv_write(log_data)
    except PermissionError:
        print(
            "PermissionError: Log not written, please close the log file."
        )
    # Clear the terminal of annoying
    # headless chrome readout and print status
    os.system("cls" if os.name == "nt" else "clear")
    print(
        f"Job Name:      {project_name}\n",
        f"Run:           {run_count}\n",
        f"Loop number:   {loop_count}\n",
        f"Time:          {log_data[2]}\n",
        f"Event          {event}\n",
        f"Download Time: {download_time}",
    )


def get_html_target():
    """Downloads target html"""
    html_state, download_time = getHTML.get_html(url)

    html_target = str(
        html_state.find_all(
            target_name, class_=target_class
        )
    )

    return html_state, html_target, download_time


def get_old_html():
    """Load original html state and back up"""
    html_state, html_target, get_html_time = (
        get_html_target()
    )

    # Save backup of current html state
    now_str = str(datetime.now()).replace(":", "-")
    html_state_filename = os.path.join(
        log_path, f"html_state_{now_str}.html"
    )

    with open(html_state_filename, "w+") as html_state_file:
        html_state_file.write(
            str(html_state.encode("utf-8"))
        )
    return html_target


def get_new_html():
    """Load a current copy of the html target"""
    html_state, html_target, get_html_time = (
        get_html_target()
    )
    return html_target, get_html_time


def send_email():
    """Send notification via gmail account"""
    sender = user
    recipients = (
        recipient
        if isinstance(recipient, list)
        else [recipient]
    )
    subject = f"Web-page change detected: {project_name}"
    message = (
        f"A change was found on the following page you are tracking: {str(url)}"
        f"\nRun: {str(run_count)}"
        f"\nLoop: {str(loop_count)}"
    )

    # Prepare actual message
    message = f"Subject: {subject}\n\n{message}"
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(user, pwd)
        server.sendmail(sender, recipients, message)
        server.close()
        log("email sent")
    except:
        log("email failed")


def sleep(short, long):
    """Randomize breaks between loops"""
    sleep_time = random.randint(short, long)
    for x in reversed(range(sleep_time)):
        b = x + 1
        print(
            "Sleep:",
            str(b) + "/" + str(sleep_time),
            "    ",
            end="\r",
        )
        time.sleep(1)


script_path = os.path.dirname(os.path.realpath(__file__))

try:
    # Set variables from YAML
    with open(script_path + "\\config.yaml") as config:
        conf = yaml.load(config)

        project_name = conf["project_name"].replace(
            " ", "-"
        )
        url = conf["url"]
        target_name = conf["target"]["name"]
        target_class = conf["target"]["class"]
        user = conf["sender"]["user"]
        pwd = conf["sender"]["pwd"]
        recipient = conf["recipient"]
        sleep_min = conf["sleep"]["min"]
        sleep_max = conf["sleep"]["max"]

        # Verify url from config is a valid url
        re_email = (
            r"^(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)"
            r"+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+$"
        )
        if not re.match(re_email, url):
            print("Regex match error: url\n", url)
            raise Exception("Regex match error")
        # Verify emails from config is valid
        re_email = (
            r"^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]"
            r"{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+)"
            r")([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$"
        )
        if not re.match(re_email, user):
            print("Regex match error: user email\n", user)
            raise Exception("Regex match error")
        for email in recipient:
            if not re.match(re_email, email):
                print(
                    "Regex match error: user email\n", user
                )
except Exception as e:
    print("There was a problem loading your YAML File.")
    raise

log_path = os.path.join(script_path, project_name)
log_file_name = f"log_{project_name}.csv"
log_file_path = os.path.join(log_path, log_file_name)
pickle_file = os.path.join(log_path, "run_count.pickle")

# Load pickled count of how many checks we have made
try:
    with open(pickle_file, "rb") as p:
        run_count = pickle.load(p)
except:
    run_count = 1
loop_count = 0  # Count of total downloads

# Log start time
log("start")

# Get current html state
old_html = get_old_html()

while True:
    loop_count += 1
    new_html, download_time = get_new_html()

    if old_html == new_html:
        log(
            "no change",
            loop_count=loop_count,
            download_time=download_time,
        )
        sleep(sleep_min, sleep_max)
    else:
        send_email()
        log(
            "change detected",
            loop_count=loop_count,
            download_time=download_time,
        )

        run_count += 1
        with open(pickle_file, "wb") as p:
            pickle.dump(run_count, p)
        # Start again
        old_html = get_old_html()
