#!/usr/bin/env python
#-*- coding:utf-8 -*-

# standard lib
import pexpect
import cPickle as pkl

# custom lib
import db_options as db
import util_functions as util


def get_url(item):
    paras = pkl.loads(item[6].encode("utf-8"))
    data = {}
    if item[4] == "GET":
        url = util.concat_url(item[5], paras)
        data = paras
        return (url, data, 'GET')
    else:
        url = item[5]
        data = paras
        return (url, data, 'POST')


def run(thread_name, item):
    url, data, method = get_url(item)
    some_stuff = ["how do you want to proceed?", pexpect.EOF, pexpect.TIMEOUT, "Do you want to follow?"]
    variable_count = [pexpect.EOF, pexpect.TIMEOUT, ]
    stuff_map = {0: "c", 1: "", 2: "", 3: "n"}
    url = '"' + url + '"'
    end = False
    injectable_point = []
    for index, key in enumerate(data):
        string = "'%s' might be injectable" % key[0]
        some_stuff.append(string)
        variable_count.append("parameter '%s'" % key[0])
        stuff_map[index+4] = key[0]

    if method == "POST":
        pass
        # TODO POST
    else:
        s = "/home/reaper/software/sqlmapproject-sqlmap-1e7f2d6/sqlmap.py -u %s" % url
        print s
        command = pexpect.spawn(s)
        count = 0
        while True:
            print "start:---------------------------------"
            index = command.expect(variable_count, timeout=120)
            print index
            if index == 0:
                pass
            elif index == 1:
                pass
            else:
                count += 1
                if count == len(data):
                    print "ddddddddddddd"
                    end = True
            print "end:---------------------------------"

            index = command.expect(some_stuff, timeout=120)
            if index == 0:
                command.sendline(stuff_map[0])
            elif index == 1 or index == 2:
                return [0, ]  #TODO
            elif index == 3:
                command.sendline(stuff_map[3])
            else:
                injectable_point.append(stuff_map[key][0])

            if end:
                return [1, injectable_point, command.before + command.after]

if __name__ == "__main__":
    run("test", "http://www.taobao.com/?id='dsaa'")
