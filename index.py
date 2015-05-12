#!/usr/bin/env python
# -*- coding:utf-8 -*-

# third-party web frame lib
from flask import Flask, render_template, request, session, jsonify
from flask.ext.socketio import SocketIO, emit
#standard lib
import os
import cPickle as pkl
import time
# custom lib
import db_options as do
from scan_manager import ScanManager
from plugins_manager import load_plugins
import util_functions as util
app = Flask(__name__)
app.secret_key = os.urandom(24)

socketio = SocketIO(app)

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
            plugins = load_plugins()
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
                check_types = ['scan',]
                info = do.db_get_check_types(conn, username, url[0])
                if info:
                    for i in info[0][:-1].split(','):
                        check_types.append(i)
                    process_info[url[0]] = {"check_types": check_types}
            return jsonify(process_info)
        else:
            return "error"


@app.route("/get_history", methods=["post"])
def get_history():
    if request.method == "POST":
        username = ""
        if 'username' in session:
            username = session['username']
            conn = do.db_connect()
            fields = do.db_get_history_field(conn)
            history = do.db_get_history(conn, username)
            do.db_close(conn)
            return jsonify({"fields": fields, "history": history})
        else:
            return "need login"
        
@app.route("/get_email", methods=["post"])
def get_email():
    if request.method == "POST":
        username = ""
        if 'username' in session:
            username = session['username']
            conn = do.db_connect()
            email = do.db_user_get_email(conn, username)
            do.db_close(conn)
            return email
        else:
            return "need login"

@app.route("/change_user_info", methods=['post'])
def change_user_info():
    if request.method == "POST":
        username = ""
        results = {}
        if 'username' in session:
            username = session['username']
            conn = do.db_connect()
            field_check = 0
            if request.form['old_pass']:
                old_pass = request.form['old_pass']
                result = do.db_match_pass(conn, old_pass ,username)
                if result == False:
                    return "-1"
            else:
                field_check += 1
            if request.form['email']:
                email = request.form['email']
                result = do.db_update_email(conn, email ,username)
                if result == 1:
                    results['email'] = "1"
                else:
                    results['email'] = "0"
            else:
                field_check += 1
            if request.form['new_pass']:
                new_pass = request.form['new_pass']
                result = do.db_update_pass(conn, new_pass ,username)
                if result == 1:
                    results['pass'] = "1"
                else:
                    results['pass'] = "0"
            else:
                field_check += 1
            if field_check == 3:
                return "2"
            return jsonify(results)
        else:
            return "need login"

@app.route("/register_form", methods=["post"])
def register():
    if request.method == "POST":
        username = request.form['register_username']
        passwd = request.form['register_password']
        email = request.form['register_email']
        if username and passwd and email:
            conn = do.db_connect()
            result = do.db_add_user(conn, username, passwd, email)
            return result
        else:
            return "-1"
        
@socketio.on('message')
def handle_message(message):
    print message['data']

@socketio.on('get_all_status')
def get_all_status():
    if 'username' in session:
        username = session['username']
        conn = do.db_connect()
        all_status = dict()
        urls = do.db_get_user_roots(conn, username)
        for url in urls:
            keys, values = do.db_get_all_status(conn, username, url[0])
            keys = keys.split(",")
            items = dict()
            for index, key in enumerate(keys):
                items[key] = str(values[index])

            if values.count(0) == len(values):
                items["total_status"] = "0"
            if values.count(2) == len(values):
                items["total_status"] = "2"
            if values.count(0) != 0:
                items["total_status"] = "1"
            if values.count(-1) != 0:
                items["total_status"] = "-1"
            all_status[url[0]] = items
            time.sleep(0.04)
        emit("get_all_status", all_status)

@socketio.on('get_status_info')
def get_status_info(data):
    if 'username' in session:
        username = session['username']
        conn = do.db_connect()
        root = data['url_info']
        count = data['count']
        pre_needed_type = data['type_info']

        start_i = pre_needed_type.find('_') + 1
        end_i = pre_needed_type.find('_second_panel')
        needed_type = pre_needed_type[start_i:end_i]
        if needed_type == 'scan':
            pre_info = do.db_get_requests_url(conn, username, root, count)
            if pre_info:
                paras = pkl.loads(pre_info[1].encode("utf-8"))
                deal_info = util.concat_url(pre_info[0], paras)
                info = {"url": deal_info, "status": "ok"}
            else:
                info = ""
        else:#TODO
            pre_info = do.db_get_url_status(conn, username, root, needed_type)
            if pre_info:
                paras = pkl.loads(pre_info[1].encode("utf-8"))
                deal_info = util.concat_url(pre_info[0], paras)
                status = pre_info[2]
                if status == 1:
                    status = "doing"
                else:
                    status = pre_info[2]
                info = {"url": deal_info, "status": status}
            else:
                info = ""
        emit("get_status_info", {"result": info})




if __name__ == "__main__":
    socketio.run(app)
