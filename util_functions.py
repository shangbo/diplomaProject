#!/usr/bin/env python
#-*- coding:utf-8 -*-

#standard
import subprocess
import sys
#custom lib
import db_options as db_op


def deal_page(thread_name, link):
    if isinstance(link, tuple):
        link = link[0]
    casperjs_para = "".join(["--root_url=",link])
    proc = subprocess.Popen(["casperjs", "tencent.js", casperjs_para], stdout=subprocess.PIPE)
    return proc.communicate()[0]

def request_store(thread_name, info):
    conn = db_op.db_connect()
    db_op.db_store_request(conn, info)
    db_op.db_close(conn)
    return 1

def usage():
    print "Usage: %s [--root_url='url' --number='link_number'] " % sys.argv[0]