#!/usr/bin/env python
# -*- coding:utf-8 -*-

#third-party web frame lib
from flask import Flask, render_template, request, session
import os

#custom lib
import db_options as do
from scan_manager import ScanManager

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route("/")
def login_page():
    return render_template("login.html")

@app.route("/submit_page.html", methods=["POST"])
def index():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        conn = do.db_connect()
        info = do.db_check_login(conn, username, password)
        if info[0] == 1:
            session['username'] = username
            return render_template("submit_page.html")
        elif info[0] == 0:
            return "login failed"
        else:
            return "bad request"


@app.route("/submit_form.html", methods=["POST"])
def submit_form():
    if request.method == "POST":
        username = ""
        if 'username' in session:
            username = session['username']
            check_types = ""
            url = request.form["url_string"]
            request_number = request.form["request_num"]
            thread_number = request.form["thread_num"]
            if request_number:
                request_number = int(request_number)
            else:
                request_number = 400            
            if thread_number:
                thread_number = int(thread_number)
            else:
                thread_number = 10
            if "xss" in request.form:
                check_types += "xss,"
            if "sql" in request.form:
                check_types += "sql,"
            if "cms" in request.form:
                check_types += "cms,"
            rm = ScanManager(thread_num=thread_number, request_num=request_number, root_url=url, check_types=check_types, username=username)
            rm.do_scan()
            return "1" #successful
        else:
            return "-1" #need login
    else:
        return "method error"

@app.route("/is_repeat_scan.html", methods=["POST"])
def is_repeat():
    if request.method == "POST":
        username = ""
        if 'username' in session:
            username = session['username']
            root = request.form['root']
            conn = do.db_connect()
            count = do.db_get_count(conn, root, username)
            if count:
                return "1"
            else:
                return "0"
        else:
            return "error"




if __name__ == "__main__":
    app.run(debug=True)