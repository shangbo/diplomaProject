#!/usr/bin/env python
#-*- coding:utf-8 -*-

import threading
import Queue
import sys
import time
import subprocess

class Worker(threading.Thread):
    worker_count = 0
    def __init__(self, work_queue, time_out=5):
        Worker.worker_count += 1
        self._id = Worker.worker_count
        threading.Thread.__init__(self,name="worker_%d" % self._id)
        self.work_queue = work_queue
        self.time_out = time_out
        self.setDaemon(True)
        self.start()

    def run(self):
        while True:
            try:
                callback, args = self.work_queue.get(timeout = self.time_out)
                res = callback(self.getName(), args)
                if res != 1:
                    self._deal_info(res)
            except Queue.Empty:
                print "".join([self.getName(),":no task\n"])
            except:
                print "thread %d had some error: %s" % (self._id, sys.exc_info()[:2])

    def _deal_info(self, result):
        result_list = result.split("\n")
        for item in result_list:
            if item.startswith("New"):
                self._deal_new_link(item)
            if item.startswith("GET"):
               self._deal_get_request(item) 
            # TODO IF POST

    def _deal_new_link(self, item):
        link = ""
        arg0 = item.split(": ")
        if len(arg0) == 2 and arg0[1].startswith("http"):
            link = arg0[1]
        if link:
            self.work_queue.put((deal_page, link))

    def _deal_get_request(self, item):
        link = ""
        arg0 = item.split(": ")                
        if len(arg0) == 2 and arg0[1].startswith("http"):
            link = arg0[1]
        if link and link.find("?") != -1:
            link_tuple = link.split("?")
            if len(link_tuple) == 2:
                link, para_str = link_tuple
            else:
                link = link_tuple[0]
                para_str = "".join(list(link_tuple[1:]))
            paras = []
            if not (link.endswith(".js") or link.endswith(".css")):
                print link
                if para_str.find("&") != -1:
                    para_list = para_str.split("&")
                    for para_item in para_list:
                        if para_item.find("=") != -1:
                            arg1 = tuple(para_item.split("="))
                            paras.append(arg1)
                    if paras:
                        print paras
                        self.work_queue.put((request_store, (link, paras)))
                else:
                    if para_str.find("=") != -1:
                        paras.append(tuple(para_str.split("=")))
                        print paras
                        self.work_queue.put((request_store, (link, paras)))
            print "-----------------"
        else:
            if not (link.endswith(".js") or link.endswith(".css")):
                self.work_queue.put((deal_page, link))
                
class ThreadPool(object):
    """ 
        TODO
    """
    def __init__(self, worker_num=10):
        self.work_queue = Queue.Queue()
        self.workers = []
        self.worker_num = worker_num
        self._recruit_threads()

    def _recruit_threads(self):
        for i in range(self.worker_num):
            worker = Worker(self.work_queue)   
            self.workers.append(worker)

    def add_job(self, callback, *args):
        self.work_queue.put((callback, args))

    def wait_for_complete(self):
        while len(self.workers):
            # print u"链接队列长度:", self.work_queue.qsize()
            worker = self.workers.pop()
            worker.join()
            if worker.is_alive() and not self.work_queue.empty():
                self.worker.append(worker)

def deal_page(thread_name, link):
    if isinstance(link, tuple):
        link = link[0]
    casperjs_para = "".join(["--root_url=",link])
    proc = subprocess.Popen(["casperjs", "tencent.js", casperjs_para], stdout=subprocess.PIPE)
    return proc.communicate()[0]

def request_store(thread_name, info):
    return 1
    


if __name__ == "__main__":
    tp = ThreadPool()
    tp.add_job(deal_page, "http://www.qq.com")
    tp.wait_for_complete()