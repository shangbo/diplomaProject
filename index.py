#!/usr/bin/env python
# -*- coding:utf-8 -*-

# third-party web frame lib
from flask import Flask, render_template, request, session, jsonify

#standard lib
import os


# custom lib
import db_options as do
from scan_manager import ScanManager
from util_functions import load_plugins_to_show

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
            pre_plugins = load_plugins_to_show()
            plugins = []
            for p in pre_plugins:
                plugins.append(p[:-3])
            return render_template("submit_page.html",plugins=plugins)
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
            for i in request.form:
                if i.startswith("mod_"):
                    check_types += i
                    check_types += ','
            rm = ScanManager(thread_num=thread_number, request_num=request_number,
                             root_url=url, check_types=check_types, username=username)
            rm.do_scan()
            return "1"  # successful
        else:
            return "-1"  # need login
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
            return "need login"


@app.route("/get_process_info", methods=["POST"])
def get_process_info():
    if request.method == "POST":
        username = ""
        if 'username' in session:
            process_info = {}
            username = session['username']
            conn = do.db_connect()
            urls = do.db_get_user_roots(conn, username)
            for url in urls:
                check_types = ['Scan',]
                info = do.db_get_check_types(conn, username, url[0])
                if info:
                    for i in info[0][:-1].split(','):
                        check_types.append(i)
                    process_info[url[0]] = {"check_types": check_types}
            return jsonify(process_info)
        else:
            return "error"

@app.route("/get_status_info", methods=["POST"])
def get_status_info():
    if request.method == "POST":
        username = ""
        if 'username' in session:
            username = session['username']
            conn = do.db_connect()
            root = request.form['url_info']
            pre_needed_type = request.form['type_info']

            start_i = pre_needed_type.find('_') + 1
            end_i = pre_needed_type.find('_second_panel')
            needed_type = pre_needed_type[start_i:end_i]
            if needed_type == 'Scan':
                info = do.db_get_requests(conn, username, root)
            else:
                info = do.db_get_url_status(conn, username, root, needed_type)
            result = []
            for i in info:
                result.append(i[0])
            print result
            return jsonify({"result":result})
        else:
            return "need login"

if __name__ == "__main__":
    app.run(debug=True,port=5000)
