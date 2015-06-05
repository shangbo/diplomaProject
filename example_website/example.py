#/usr/bin/env python
#-*- coding:utf-8 -*-
__author__ = 'reaper'

from flask import Flask, render_template, request, session, jsonify
import os
import MySQLdb as m_db

app = Flask("example")
app.secret_key = os.urandom(24)

@app.route("/")
def index():
    return render_template("example.html")

@app.route("/sql_injection")
def sql_injection():
    _id = request.args.get("id", "")
    username = request.args.get("user", "")
    conn = db_connect()
    info = db_query_request(conn, _id, username)
    db_close(conn)
    return str(info)

@app.route("/xss_injection")
def xss_injection():
    _rr = request.args.get("rr")
    return _rr

def db_connect():
    conn = m_db.connect(host="localhost", user="root", passwd="shangbo123", db="request_spider", charset="utf8")
    return conn


def db_close(conn):
    conn.close()

def db_query_request(conn, _id, username):
    cursor = conn.cursor()
    read_sql = '''select * from requests where _id=%s and username="%s" ''' % (_id, username)
    print read_sql
    cursor.execute(read_sql)
    info = cursor.fetchone()
    cursor.close()
    return info

if __name__ == "__main__":
    app.run(debug=True, port=8000)