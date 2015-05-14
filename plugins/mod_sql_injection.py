#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys
sys.path.insert(0, "..")
# standard lib
import pexpect
import cPickle as pkl

# custom lib
import util_functions as util


def get_url(item):
    paras = pkl.loads(item[6].encode("utf-8"))
    if item[4] == "GET":
        url = util.concat_url(item[5], paras)
        data = paras
        return url, data, 'GET'
    else:
        url = item[5]
        data = paras
        return url, data, 'POST'


def run(thread_name, item):
    url, data, method = get_url(item)
    some_stuff = ["how do you want to proceed?", pexpect.EOF, pexpect.TIMEOUT, "Do you want to follow?"]
    stuff_map = {0: "c", 1: "", 2: "", 3: "n"}
    url = '"' + url + '"'
    injectable_point = []
    for index, key in enumerate(data):
        string = "'%s' is injectable" % key[0]
        some_stuff.append(string)
        some_stuff.append("[WARNING] GET parameter '%s'" % key[0])
        stuff_map[some_stuff.index(string)] = key[0]

    if method == "POST":
        pass
        # TODO POST
    else:
        s = "/home/reaper/software/sqlmapproject-sqlmap-1e7f2d6/sqlmap.py -u %s" % url
        print s
        command = pexpect.spawn(s)
        log = ""
        count = 0
        while True:
            index = command.expect(some_stuff, timeout=150)
            print index
            if index == 0:
                before = command.before
                after = command.after
                log += before
                log += after
                command.sendline(stuff_map[0])
            elif index == 1:
                if isinstance(command.before, type):
                    before = "\n EOF!"
                else:
                    before = command.before + "\n EOF"
                if isinstance(command.after, type):
                    after = "\n EOF"
                else:
                    after = command.after + "\n EOF!"
                log += before
                log += after
                return [-1, "EOF", before + after, []]
            elif index == 2:
                if isinstance(command.before, type):
                    before = "\n TimeOut!"
                else:
                    before = command.before + "\n TimeOut!"
                if isinstance(command.after, type):
                    after = "\n TimeOut!"
                else:
                    after = command.after + "\n TimeOut!"
                log += before
                log += after
                return [-1, "TimeOut", before + after, []]
            elif index == 3:
                before = command.before
                after = command.after + "\n EOF!"
                log += before
                log += after
                command.sendline(stuff_map[3])
            else:
                before = command.before
                after = command.after
                log += before
                log += after
                if some_stuff[index].startswith("[WARNING]"):
                    count += 1
                else:
                    injectable_point.append(stuff_map[index])

            if count == len(data):
                return [len(injectable_point), "Normal", log, injectable_point]

if __name__ == "__main__":
    pass