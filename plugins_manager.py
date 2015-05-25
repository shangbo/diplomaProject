#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys
import Queue
import threading
import imp
from xml.etree.ElementTree import Element, SubElement, tostring, parse
from xml.dom import minidom
import md5
import cPickle as pkl
import time

import util_functions as util
import db_options as do
mylock = threading.RLock()

ISOTIMEFORMAT = '%Y-%m-%d %X'

class PluginsManager(object):
    def __init__(self, worker_num, root_url, username, check_types):
        self.wait_queue = Queue.Queue()
        self.workers = []
        self.worker_num = 1
        self.root_url = [root_url, ]
        self.username = username
        self.check_types = check_types
        self.stop_flag = [False, ]
        self._init_xml_files()
        t = threading.Thread(target=self._auto_add_jobs)
        t.start()
        self._recruit_threads()

    def _recruit_threads(self):
        for i in range(self.worker_num):
            worker = PluginWorker(self.wait_queue, self.stop_flag)
            self.workers.append(worker)
        print "init threads file finished"

    def _init_xml_files(self):
        check_types = self.check_types.split(',')
        for mod_name in check_types:
            if mod_name:
                root = Element('Buglist')
                root.set("coding", 'utf-8')
                root.set("root_url", self.root_url[0])
                root.set("username", self.username)
                root.set("type", mod_name)
                rough_xml = tostring(root, 'utf-8')
                reparsed = minidom.parseString(rough_xml)
                m = md5.new()
                m.update(self.username + self.root_url[0] + mod_name)
                xml_file_name = m.hexdigest() + '.xml'
                with open("./report/" + xml_file_name, 'w') as f:
                    f.write(reparsed.toprettyxml(indent="  "))
        print "init xml file finished"

    def _auto_add_jobs(self):
        check_types = self.check_types.split(',')
        types_run_function = {}
        for mod_name in check_types:
            if mod_name:
                fp, pathname, desc = imp.find_module(mod_name, ['./plugins', ])
                mod_instance = imp.load_module(mod_name, fp, pathname, desc)
                run_function = getattr(mod_instance, 'run')
                types_run_function[mod_name] = run_function
        conn = do.db_connect()
        info = do.db_get_all_requests(conn, self.username, self.root_url[0])
        count = 1
        for i in info:
            for func_index in types_run_function:
                count += 1
                self.wait_queue.put((types_run_function[func_index], i))
        do.db_close(conn)
        print "add jobs finished"

    def wait_for_complete(self):
        while len(self.workers):
            if not self.stop_flag[0]:
                worker = self.workers.pop()
                worker.join()
                if worker.is_alive() and not self.wait_queue.empty():
                    self.workers.append(worker)
            else:
                self.workers = []
                break
        conn = do.db_connect()
        do.db_update_end_time(conn, self.username, self.root_url[0], time.strftime(ISOTIMEFORMAT, time.localtime()))
        do.db_close(conn)
        del self


class PluginWorker(threading.Thread):
    worker_count = 0
    def __init__(self, wait_queue, stop_flag, time_out=5):
        PluginWorker.worker_count += 1
        self._id = PluginWorker.worker_count
        threading.Thread.__init__(self,name="plugin_worker_%d" % self._id)
        self.wait_queue = wait_queue
        self.stop_flag = stop_flag
        self.time_out = time_out
        self.setDaemon(True)
        self.start()


    def run(self):
        while not self.stop_flag[0]:
            try:
                callback, args = self.wait_queue.get(timeout=self.time_out)
                conn = do.db_connect()
                do.db_update_plugin_status(conn, 1, callback.__module__, args[0])
                res = callback(self.getName(), args)
                m = md5.new()
                m.update(args[1] + args[2] + callback.__module__)
                xml_file_name = m.hexdigest()
                mylock.acquire()
                ele = parse("./report/" + xml_file_name + '.xml')
                mylock.release()
                buglist = ele.getroot()
                bug = SubElement(buglist, "Bug")
                paras = pkl.loads(args[6].encode("utf-8"))
                url = util.concat_url(args[5], paras)
                url_ele = SubElement(bug, "url")
                url_ele.text = url
                status = SubElement(bug, "Status")
                status.text = res[1]
                status = SubElement(bug, "log")
                status.text = res[2]
                rough_xml = tostring(buglist, 'utf-8')
                # reparsed = minidom.parseString(rough_xml)

                mylock.acquire()
                with open("./report/" + xml_file_name + '.xml', "w") as f:
                    # print reparsed.toprettyxml(indent="  ")
                    f.write(rough_xml)
                mylock.release()

                if res[0] == -1:
                    do.db_update_plugin_status(conn, -1, callback.__module__, args[0])
                else:
                    do.db_update_plugin_status(conn, res[0] + 2, callback.__module__, args[0])

                total_status = do.db_get_urls_current_status(conn, args[1], args[2], callback.__module__)
                do.db_update_plugin_total_status(conn, total_status, callback.__module__, args[1], args[2])
                do.db_close(conn)
            except Queue.Empty:
                self.stop_flag[0] = True
            except:
                print "thread %s had some error: %s" % (self.getName(), sys.exc_info())
        else:
            while not self.wait_queue.empty():
                self.wait_queue.get()
            print "".join([self.getName(), " finished"])


def load_plugins():
    try:
        pre_plugins = os.listdir('./plugins') #hard Write
    except OSError:
        pre_plugins = os.listdir('./diplomaProject/plugins') #hard Write
    plugins = []
    for p in pre_plugins:
        if p.startswith("mod") and p.endswith(".py"):
            plugins.append(p[:-3])
    return plugins

def is_plugin_exist(plugin_name):
    plugins_list = load_plugins()
    if plugin_name in plugins_list:
        return True
    else:
        return False

if __name__ == '__main__':
    pm = PluginsManager(1, "http://www.taobao.com", "loftysoul", "mod_xss,")
    pm.wait_for_complete()