#!/usr/bin/env python
# -*- coding:utf-8 -*-

import smtplib
import email.utils
import email.encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from db_options import db_get_user_email, db_close, db_connect

#global var
MAIL_SERVER_NAME = 'smtp.163.com'
USERNAME = 'shangbo808@163.com'
PASSWORD = 'sbcheerup123'
BASIC_PATH = './'


# identify message
def get_main_body():
    try:
        f = open(BASIC_PATH+'templates/mail.html', 'r+')
    except IOError:
        f = open('templates/mail.html', 'r+')
    text = f.read()
    f.close()
    msg_text = MIMEText(text, _subtype='html')

    return msg_text


def get_report(reports_name):
    msg_reports = []
    for report_name in reports_name:
        try:
            f = open(BASIC_PATH+'report/'+report_name, 'r')
        except IOError:
            f = open('report/'+report_name, 'r')
        report = f.read()
        f.close()
        msg_report = MIMEText(report)
        msg_report.add_header('Content-Disposition', 'attachment', filename='result.xml')
        msg_reports.append(msg_report)
    return msg_reports


def get_msg(main_body, reports):
    msg_main = MIMEMultipart()
    msg_main.attach(main_body)
    for report in reports:
        msg_main.attach(report)

    return msg_main


def set_header(msg_main, to_email):
    msg_main.set_unixfrom('soul')
    msg_main['To'] = email.utils.formataddr(('Dear', to_email))
    msg_main['From'] = email.utils.formataddr(('loftysoul', 'shangbo808@163.com'))
    msg_main['Subject'] = 'Vulnerability Check Result'
    msg_main['Date'] = email.utils.formatdate()


def send_email(msg_main,to_email):
    server = smtplib.SMTP(MAIL_SERVER_NAME)
    try:
        server.set_debuglevel(True)
        server.ehlo()
        if server.has_extn('STARTTLS'):
            server.starttls()
            server.ehlo()
        server.login(USERNAME, PASSWORD)
        server.sendmail('shangbo808@163.com', [to_email], msg_main.as_string())
    finally:
        server.quit()


def mail_main(username, reports_name):
    conn = db_connect()
    to_email = db_get_user_email(conn, username)
    db_close(conn)
    print 'send email to ', to_email
    msg_text = get_main_body()
    msg_file_reports = get_report(reports_name)
    msg_main = get_msg(msg_text, msg_file_reports)
    set_header(msg_main, to_email)
    send_email(msg_main, to_email)


if __name__ == '__main__':
    mail_main("loftysoul", ["79c2a339dc26bf110bb0f8d6e7317ba2.xml", ])
