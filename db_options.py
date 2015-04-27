#/usr/bin/env python
# -*- coding:utf-8 -*-

import MySQLdb as m_db


def db_connect():
    conn = m_db.connect(host="localhost", user="root", passwd="shangbo123", db="request_spider", charset="utf8")
    return conn

def db_close(conn):
    conn.close()

def db_store_request(conn, info):
    cursor = conn.cursor()
    write_sql = '''insert into requests(root, method, _date, md5, url, keys_values, sql_injection) values("%s", "%s", "%s", "%s", "%s", "%s", 0)''' % info
    print write_sql    
    cursor.execute(write_sql)
    conn.commit()
    cursor.close()

def db_check_md5(conn, md5):
    cursor = conn.cursor()
    read_sql = "select * from requests where md5='%s'" % md5
    cursor.execute(read_sql)
    print cursor.fetchone()
    if cursor.fetchone():
        cursor.close()
        return 1
    else:
        cursor.close()
        return 0

def db_get_sql_injection_url(conn):
    cursor = conn.cursor()
    read_sql =  ''' select * from requests where sql_injection = 0'''
    cursor.execute(read_sql)
    info = cursor.fetchall()
    cursor.close()
    return info


def db_get_count(conn):
    cursor = conn.cursor()
    read_sql = "select * from requests"
    cursor.execute(read_sql)
    info = cursor.fetchone()
    return info[0]