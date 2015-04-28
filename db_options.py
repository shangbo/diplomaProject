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
    write_sql = '''insert into requests(username, root, method, _date, md5, url, keys_values, sql_injection) values("%s", "%s", "%s", "%s", "%s", "%s", "%s", 0)''' % info
    cursor.execute(write_sql)
    conn.commit()
    cursor.close()

def db_check_md5(conn, md5):
    cursor = conn.cursor()
    read_sql = "select * from requests where md5='%s'" % md5
    cursor.execute(read_sql)
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


def db_get_count(conn, root_url, username):
    cursor = conn.cursor()
    root = ""
    if isinstance(root_url, list):
        root_url = root_url[0]
    read_sql = "select count(*) from requests where username='%s' and root='%s'" % (username, root_url)
    cursor.execute(read_sql)
    info = cursor.fetchone()
    return info[0]
    return 0

def db_check_login(conn, username, password):
    cursor = conn.cursor()
    read_sql =  ''' select count(*) from user_info where username='%s' and passwd="%s"'''  % (username,password)
    cursor.execute(read_sql)
    info = cursor.fetchone()
    cursor.close()
    return info

def db_store_scan_info(conn, scan_info):
    cursor = conn.cursor()
    write_sql = '''
    insert into user_scan_record(username, root, request_num, thread_num, connection_status, scan_status, sql_status, xss_status, cms_status, start_time) 
    values('%s','%s', %d, %d, %d, 0, %d, %d, %d, '%s') 
    ''' % scan_info
    cursor.execute(write_sql)
    conn.commit()
    cursor.close()

def db_update_scan_status(conn, status):
    cursor = conn.cursor()
    update_sql = '''update user_scan_record set scan_status=%d''' % status
    cursor.execute(update_sql)
    conn.commit()
    cursor.close()    