#!/usr/bin/env python
#-*- coding:utf-8 -*-

# standard lib
import subprocess
import cPickle as pkl

#custom lib
import db_options as db


def get_url(item):
    paras =  pkl.loads(item[5].encode("utf-8"))
    data = {}
    if item[3] == "GET":
        url = _concat_url(item[4], paras)
    else:
        url = item[4]
        data = paras
    return (url, data)
    

def _concat_url(url, paras):
    url_string = url + "?"
    for item in paras:
        url_string = url_string + item[0] + "=" + item[1] + "&"
    url_string = url_string[:-1]
    return url_string

def execute_sqlmap(item):
    url, data = get_url(item)
    if data:
        pass
        #TODO POST
    else:
        print url
        proc = subprocess.Popen(["sqlmap", "-u", url], stdout=subprocess.PIPE)
        print proc.communicate()[0]

def main():
    conn = db.db_connect()
    info = db.db_get_sql_injection_url(conn)
    db.db_close(conn)
    for item in info:
        execute_sqlmap(item)

if __name__ == "__main__":
    main()
