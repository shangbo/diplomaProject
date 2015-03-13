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
                callback, args, kwds = self.work_queue.get(timeout = self.time_out)

                res = callback(self.getName(), *args, **kwds)
                if res != 1:
                    self._deal_info(res)

            except Queue.Empty:
                print "".join([self.getName(),":task complete\n"])
            except:
                print "thread %d had some error: %s" % (self._id, sys.exc_info()[:2])

    def _deal_info(self, result):
        result_list = result.split("\n")
        print len(result_list)
        for item in result_list:
            link = item.split(": ")[1]
            print link
            # if item.startswith("New"):
            #     print "."
            #     self.work_queue.put((deal_page, link))
            # if item.startswith("GET"):
            #     if link.find("?"):
            #         link, para_str = link.split("?")
            #         paras = []
            #         if para_str.find("&"):
            #             para_list = para_str.split("&")
            #             for para_item in para_list:
            #                 paras.append(para_item[:para_item.find("=")])
            #             self.work_queue.put((request_store, link, paras))
            #         else:
            #             paras.append(para_str[:para_str.find("=")])
            #             self.work_queue.put((request_store, link, paras))
            #     else:
            #         self.work_queue.put((deal_page, link))
            #TODO IF POST

                
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

    def add_job(self, callback, *args, **kwds):
        self.work_queue.put((callback, args, kwds))

    def wait_for_complete(self):
        while len(self.workers):
            worker = self.workers.pop()
            worker.join()
            if worker.is_alive() and not self.work_queue.empty():
                self.worker.append(worker)
        print "nidayede !!!!!!!!!!!!!!!!!!!!!1\n"

def deal_page(thread_name, link):
    print thread_name
    casperjs_para = "".join(["--root_url=",link])
    proc = subprocess.Popen(["casperjs", "tencent.js", casperjs_para], stdout=subprocess.PIPE)
    return proc.communicate()[0]

def request_store():
    return 1
    


if __name__ == "__main__":
    tp = ThreadPool()
    tp.add_job(deal_page, "http://www.qq.com")
    tp.wait_for_complete()