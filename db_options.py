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
    write_sql = '''insert into requests(username, root, method, _date, md5, url, keys_values) values("%s", "%s", "%s", "%s", "%s", "%s", "%s")''' % info
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

def db_update_plugin_status(conn, status, plugin_name, _id):
    cursor = conn.cursor()
    read_sql = ''' update requests set %s=%d where _id=%d ''' % (plugin_name, status, _id)
    cursor.execute(read_sql)
    conn.commit()
    cursor.close()


def db_get_count(conn, root_url, username):
    cursor = conn.cursor()
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
    insert into user_scan_record(username, root, request_num, thread_num, connection_status, check_types, start_time) 
    values('%s','%s', %d, %d, %d, '%s', '%s') 
    ''' % scan_info
    cursor.execute(write_sql)
    conn.commit()
    cursor.close()

def db_update_scan_status(conn, status, username, root):
    cursor = conn.cursor()
    update_sql = '''update user_scan_record set scan_status=%d where username='%s' and root='%s' ''' % (status, username, root)
    cursor.execute(update_sql)
    conn.commit()
    cursor.close()    

def db_move_to_history(conn, username, root):
    cursor = conn.cursor()
    read_sql = '''select * from user_scan_record where username='%s' and root='%s' ''' % (username, root)
    cursor.execute(read_sql)
    info = cursor.fetchone()
    if info:
        check_types = info[7][:-1]
        info = list(info)[1:9]
        read_sql = '''select %s from user_scan_record where username='%s' and root='%s' ''' % (check_types, username, root)
        cursor.execute(read_sql)
        status = cursor.fetchone()
        info.extend(list(status))
        tmp_str = ""
        for i in check_types[:-1].split(','):
            tmp_str += ',%d'
        if info:
            write_sql_before = '''insert into scan_history(username, root, request_num, thread_num, connection_status, scan_status, check_types, start_time, end_time,%s)''' % check_types
            write_sql_after = ''' values('%s','%s', %d, %d, %d, %d''' + ''' ,'%s' ,'%s', 'xxxx' ''' + tmp_str + ')'
            write_sql_after = write_sql_after % tuple(info)
            write_sql =  write_sql_before + write_sql_after
            cursor.execute(write_sql)
            conn.commit()
            delete_sql = ''' delete from user_scan_record where username='%s' and root='%s' ''' % (username, root)
            cursor.execute(delete_sql)
            conn.commit()
    cursor.close()


def db_clear_repeat_scan(conn,username, root_url):
    cursor = conn.cursor()
    delete_sql = '''delete from requests where username="%s" and root="%s"''' % (username, root_url)
    cursor.execute(delete_sql)
    conn.commit()
    cursor.close()        

def db_get_user_roots(conn, username):
    cursor = conn.cursor()
    read_sql =  ''' select root from user_scan_record where username='%s' '''  % username
    cursor.execute(read_sql)
    urls = cursor.fetchall()
    cursor.close()
    return urls

def db_get_url_status(conn, username, root, needed_type):
    cursor = conn.cursor()
    read_sql = '''select url, keys_values, %s from requests where username='%s' and root='%s' and %s!=0''' % (needed_type, username, root, needed_type)
    cursor.execute(read_sql)
    info = cursor.fetchone()
    cursor.close()
    return info

def db_modify_table_structure(conn, field_name):
    cursor = conn.cursor()
    read_sql =  ''' desc user_scan_record;'''
    cursor.execute(read_sql)
    info = cursor.fetchall()
    for i in info:
        if i[0] == field_name:
            return 1
        else:
            continue
    modified_sql = 'alter table user_scan_record add %s int(1) default 0' % field_name
    cursor.execute(modified_sql)
    conn.commit()
    
    read_sql =  ''' desc scan_history;'''
    cursor.execute(read_sql)
    info = cursor.fetchall()
    for i in info:
        if i[0] == field_name:
            return 1
        else:
            continue
    modified_sql = 'alter table scan_history add %s int(1) default 0' % field_name
    cursor.execute(modified_sql)
    conn.commit()

    read_sql =  ''' desc requests;'''
    cursor.execute(read_sql)
    info = cursor.fetchall()
    for i in info:
        if i[0] == field_name:
            return 1
        else:
            continue
    modified_sql = 'alter table requests add %s int(1) default 0' % field_name
    cursor.execute(modified_sql)
    conn.commit()
    cursor.close()

def db_get_check_types(conn, username, root_url):
    cursor = conn.cursor()
    read_sql =  ''' select check_types from user_scan_record where username='%s' and root='%s' '''  % (username, root_url)
    cursor.execute(read_sql)
    info = cursor.fetchone()
    cursor.close()
    return info

def db_get_requests_url(conn, username, root_url, count):
    cursor = conn.cursor()
    read_sql =  ''' select url,keys_values from requests where username='%s' and root='%s' limit %d,1 '''  % (username, root_url, count)
    cursor.execute(read_sql)
    info = cursor.fetchone()
    cursor.close()
    return info 

def db_get_all_requests(conn, username, root_url):
    cursor = conn.cursor()
    read_sql =  ''' select * from requests where username='%s' and root='%s' '''  % (username, root_url)
    cursor.execute(read_sql)
    info = cursor.fetchall()
    cursor.close()
    return info     

def db_get_history_field(conn):
    cursor = conn.cursor()
    read_sql =  '''desc scan_history '''
    cursor.execute(read_sql)
    info = cursor.fetchall()
    field = []
    for i in info:
        field.append(i[0])
    cursor.close()
    return field

def db_get_history(conn, username):
    cursor = conn.cursor()
    read_sql =  '''select * from scan_history where username='%s' ''' % username
    cursor.execute(read_sql)
    info = cursor.fetchall()
    cursor.close()
    return info

def db_user_get_email(conn, username):
    cursor = conn.cursor()
    read_sql =  '''select email from user_info where username='%s' ''' % username
    cursor.execute(read_sql)
    info = cursor.fetchone()
    cursor.close()
    return info[0]

def db_match_pass(conn, old_pass, username):
    cursor = conn.cursor()
    read_sql =  '''select passwd from user_info where username='%s' ''' % username
    cursor.execute(read_sql)
    info = cursor.fetchone()
    cursor.close()
    if old_pass == info[0]:
        return True
    else:
        return False

def db_update_email(conn, email, username):
    cursor = conn.cursor()
    update_sql = '''update user_info set email='%s' ''' % email
    result = cursor.execute(update_sql)
    conn.commit()
    cursor.close()
    return result


def db_update_pass(conn, new_pass, username):
    cursor = conn.cursor()
    update_sql = '''update user_info set passwd='%s' ''' % new_pass
    result = cursor.execute(update_sql)
    conn.commit()
    cursor.close()
    return result

def db_add_user(conn, username, passwd, email):
    cursor = conn.cursor()
    read_sql = '''select * from user_info where username='%s' ''' % username
    cursor.execute(read_sql)
    info = cursor.fetchone()
    if info:
        return -1
    else:
        insert_sql = '''insert into user_info(username, passwd, email) values('%s', '%s', '%s')''' % (username, passwd, email)
        result = cursor.execute(insert_sql)
        conn.commit()
        return result
    cursor.close()
    
def db_get_all_status(conn, username, url):
    cursor = conn.cursor()
    read_sql = '''select check_types from user_scan_record where username='%s' and root='%s' ''' % (username, url)
    cursor.execute(read_sql)
    pre_check_types = cursor.fetchone()
    read_sql = '''select scan_status, connection_status, %s from user_scan_record where username='%s' and root='%s' ''' % (pre_check_types[0][:-1], username, url)
    cursor.execute(read_sql)
    values = cursor.fetchone()
    keys = "scan, connection_status," + pre_check_types[0][:-1]
    return keys, values

def db_get_urls_current_status(conn, username, root, check_type):
    cursor = conn.cursor()
    read_sql = '''select _id from requests where username='%s' and root='%s' and %s!=0 ''' % (username, root, check_type)
    cursor.execute(read_sql)
    if cursor.fetchone:
        read_sql = '''select _id from requests where username='%s' and root='%s' and %s=1  ''' % (username, root, check_type)
        cursor.execute(read_sql)
        if cursor.fetchone:
            return 1
        else:
            return 2
    else:
        return 0

def db_update_plugin_total_status(conn, status, plugin_name, username, root):
    cursor = conn.cursor()
    update_sql = ''' update user_scan_info set %s=%d where username='%s' and root='%s' ''' % (plugin_name, status, username, root)
    cursor.execute(update_sql)
    conn.commit()
    cursor.close()

def db_get_scan_status(conn, username, root):
    cursor = conn.cursor()
    read_sql = '''select scan_status from user_scan_info where username='%s' and root='%s' ''' %(username, root)
    cursor.execute(read_sql)
    info = cursor.fetchone()
    cursor.close()
    return info

def db_update_end_time(conn, username, root, end_time):
    cursor = conn.cursor()
    update_sql = '''update user_scan_info set end_time=%s where username='%s' and root='%s' ''' % (end_time, username, root)
    cursor.execute(update_sql)
    conn.commit()
    cursor.close()