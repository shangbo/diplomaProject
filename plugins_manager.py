#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys
import Queue
import threading
import imp

import db_options as do

class PluginsManager(object):
    def __init__(self, worker_num, root_url, username, check_types):
        self.wait_queue = Queue.Queue()
        self.workers = []
        self.worker_num = worker_num
        self.root_url = [root_url,]
        self.username = username
        self.check_types = check_types
        self.stop_flag = [False,]
        t = threading.Thread(target=self._auto_add_jobs)
        t.start()
        self._recruit_threads()
        
    def _recruit_threads(self):
        for i in range(self.worker_num):
            worker = PluginWorker(self.wait_queue, self.stop_flag)
            self.workers.append(worker)

    def _auto_add_jobs(self):
        check_types = self.check_types.split(',')
        types_run_function = {}
        for mod_name in check_types:
            if mod_name:
                fp, pathname, desc = imp.find_module(mod_name, ['./plugins',])
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
        del(self)


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
                callback, args = self.wait_queue.get(timeout = self.time_out)
                res = callback(self.getName(), args)
            except Queue.Empty:
                self.stop_flag[0] = True
            except:
                print "thread %s had some error: %s"  % (self.getName(), sys.exc_info())
        else:
            while not self.wait_queue.empty():
                self.wait_queue.get()
            print "".join([self.getName(), " finished"])



def load_plugins():
    pre_plugins = os.listdir('./plugins') #hard Write
    plugins = []
    for p in pre_plugins:
        plugins.append(p[:-3])
    return plugins

def is_plugin_exist(plugin_name):
    plugins_list = load_plugins()
    if plugin_name in plugins_list:
        return True
    else:
        return False

if __name__ == '__main__':
    pm = PluginsManager(1, "http://www.taobao.com", "loftysoul", "mod_sql_injection,")
    pm.wait_for_complete()