import os
import requests
from bs4 import BeautifulSoup
import smtplib
import csv
import datetime

# NCKU english semester grade website page
url = 'https://qrys.ncku.edu.tw/ncku_e/qrys41021.asp'
# username and password for NCKU entrance
ncku_username = os.environ.get('NCKU_USERNAME')
ncku_password = os.environ.get('NCKU_PASSWORD')
# characteristic string that allows network protocol peers to identify the Operating System and Browser of the web-server
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'
}
# form data for login request authentication
form_data = {
    'ID': ncku_username,
    'PWD': ncku_password,
    'Submit': 'Submit'
}
# login procedure
with requests.Session() as s:
    # grab User-Agent header
    s.get(url, headers=headers)
    # enter login request
    s.post(url, data=form_data, headers=headers, timeout=10)
    # get html content after login
    web_html = s.get(url, timeout=10).text


# web scrape https://qrys.ncku.edu.tw/ncku_e/qrys41021.asp
soup = BeautifulSoup(web_html, 'html.parser')

# find all table entry values in <table><tr><td><div> (in which the grades are stored)
all_entries = []
for div in soup.find_all('div'):
    entry = str(div.text.encode('utf-8'))
    all_entries.append(entry)
all_entries = all_entries[13:139]  # only include rows with the grades that matter

# parse all_entries into 2D list with [Course, Grades] per row
course_grades = []
row = []
for i, entry in enumerate(all_entries):
    # Course col at #4 posit & Grades col at #6 posit
    if (i - 4) % 14 == 0 or (i - 6) % 14 == 0:
        entry = entry.split("'")[1]
        row.append(entry)
    # at end of row, parse list
    if i != 0 and (i + 1) % 14 == 0:
        course_grades.append(row)
        row = []
# print(course_grades, end='\n\n')
# course_grades = [['WESTERN CLASSICAL MUSIC', '98'], ['AUTOMATIC CONTROL', '999'], ['EXPERIMENTS IN ELECTRONICS', '97'], ['COMBUSTION', '999'], ['FLUID MECHANICS', '94'], ['SOLAR THERMAL ENERGY', '92'], ['CONDUCT (1)', '85'], ['EXPERIMENT ON DIGITAL SYSTEM', '999'], ['WIRELESS COMMUNICATIONS AND MOBILE NETWORKS', '999']]


# read saved grades.csv which contains [Course, Grades] pairs
with open('grades.csv', 'r') as old_file:
    csv_reader = csv.reader(old_file)
    old_course_grades = []
    for line in csv_reader:
        old_course_grades.append(line)

# compare with newly scraped data and see if update is necessary
need_update = False
need_update_idx = []
for i, old_grade in enumerate(old_course_grades):
    if course_grades[i] != old_grade:
        need_update = True
        need_update_idx.append(i)
# print(need_update)
# print(need_update_idx)


# write new grades into grades.csv if new grades were posted
if need_update:
    with open('grades.csv', 'w') as new_file:
        csv_writer = csv.writer(new_file, delimiter=',')
        for row in course_grades:
            csv_writer.writerow(row)

# send email to ethanchan2416@gmail.com to notify grade update
    gmail_address = os.environ.get('GMAIL_USERNAME')
    gmail_password = os.environ.get('GMAIL_PASSWORD')

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        smtp.login(gmail_address, gmail_password)

        subject = 'NEW GRADES ANNOUNCED FOR 108-1 SEMESTER!!!'
        body = ''
        for i in need_update_idx:
            line = f'{course_grades[i][0]}: {course_grades[i][1]}\n'
            body += line
        msg = f'Subject: {subject}\n\n{body}'

        smtp.sendmail(gmail_address, 'ethanchan2416@gmail.com', msg)


# log script update timestamp into log.txt
timestamp = datetime.datetime.now()
with open('log.txt', 'a') as new_file:
    new_released = ''
    if need_update:
        for i in need_update_idx:
            line = f', {course_grades[i][0]}'
            new_released += line
        log = str(timestamp) + new_released + '\n'
    else:
        log = str(timestamp) + '\n'
    new_file.write(log)
