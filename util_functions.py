#!/usr/bin/env python
#-*- coding:utf-8 -*-

#standard
# import subprocess
import commands
import sys
#custom lib
import db_options as db_op


def deal_page(thread_name, link):
    # print thread_name + " is alive!"
    if isinstance(link, tuple):
        link = link[0]
    casperjs_para = "".join(["--root_url=",link])
    msg = commands.getstatusoutput("".join(["casperjs tencent.js " ,casperjs_para]))
    return msg[1]

def request_store(thread_name, username, info):
    conn = db_op.db_connect()
    request_info = [username, ]
    for i in info:
        request_info.append(i)
    info = tuple(request_info)
    db_op.db_store_request(conn, info)
    db_op.db_close(conn)
    return 1

def usage():
    print "Usage: %s [--root_url='url' --number='link_number'] " % sys.argv[0]