#!/usr/bin/env python
#-*- coding:utf-8 -*-

#standard 
import threading
import Queue
import sys
import time
import md5
import cPickle as pkl
import getopt

mylock = threading.RLock()

#custom lib
import db_options as db_op
from util_functions import deal_page, request_store, usage
ISOTIMEFORMAT = '%Y-%m-%d %X'

class PageWorker(threading.Thread):
    worker_count = 0
    md5_pool = []
    def __init__(self, page_queue, store_queue, root_url, request_num, stop_flag, time_out=5):
        PageWorker.worker_count += 1
        self._id = PageWorker.worker_count
        threading.Thread.__init__(self, name="page_worker_%d" % self._id)
        self.request_num = request_num
        self.stop_flag = stop_flag
        self.page_queue = page_queue
        self.store_queue = store_queue
        self.root_url = root_url
        self.time_out = time_out
        self.setDaemon(True)
        self.start()

    def run(self):
        while not self.stop_flag[0]:
            try:
                callback, args = self.page_queue.get(timeout = self.time_out)
                res = callback(self.getName(), args)
                self._deal_info(res)
            except Queue.Empty:
                break
                # print "".join([self.getName(),":no task\n"])
            except:
                print "thread %s had some error: %s"  % (self.getName(), sys.exc_info())
        else:
            while not self.page_queue.empty():
                self.page_queue.get()
            print "".join([self.getName(), " finished"])

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
            self.page_queue.put((deal_page, link))

    def _check_same_domain_name(self, url1, url2):
        if url1[0].split('/')[2].split('.')[-1] == url2.split('/')[2].split('.')[-1] and\
            url1[0].split('/')[2].split('.')[-2] == url2.split('/')[2].split('.')[-2]:
            return 1
        else:
            return 0

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
            if self._check_same_domain_name(self.root_url, link):

                if not (link.endswith(".js") or link.endswith(".css")):
                    conn = db_op.db_connect()
                    if para_str.find("&") != -1:
                        para_list = para_str.split("&") 
                        for para_item in para_list:
                            if para_item.find("=") != -1:
                                arg1 = tuple(para_item.split("="))
                                paras.append(arg1)
                        if paras:
                            m = md5.new()
                            sorted_paras = []
                            for p in paras:
                                sorted_paras.append(p[0])
                            sorted_paras.sort()
                            m.update(link+str(sorted_paras))
                            md5_string = m.hexdigest()
                            if not self.md5_pool.count(md5_string):
                            # if not db_op.db_check_md5(conn, md5_string):
                                self.md5_pool.append(md5_string)
                                para_s = pkl.dumps(paras)
                                argument = (self.root_url[0], "GET", time.strftime(ISOTIMEFORMAT, time.localtime()), md5_string, link, para_s)
                                self.store_queue.put((request_store, argument))
                            else:
                                pass
                    else:
                        if para_str.find("=") != -1:
                            paras.append(tuple(para_str.split("=")))
                            m = md5.new()
                            sorted_paras = []
                            for p in paras:
                                sorted_paras.append(p[0])
                            sorted_paras.sort()
                            m.update(link+str(sorted_paras))
                            md5_string = m.hexdigest()
                            if not self.md5_pool.count(md5_string):
                            # if not db_op.db_check_md5(conn, md5_string):
                                self.md5_pool.append(md5_string)
                                para_s = pkl.dumps(paras)
                                argument = (self.root_url[0], "GET", time.strftime(ISOTIMEFORMAT, time.localtime()), md5_string, link, para_s)

                                self.store_queue.put((request_store, argument))
                            else:
                                pass
                    db_op.db_close(conn)
                else:
                    pass
            else:
                pass
        else:
            if not (link.endswith(".js") or link.endswith(".css")):
                self.page_queue.put((deal_page, link))

class StoreWorker(threading.Thread):
    worker_count = 0
    def __init__(self, page_queue, username, store_queue, root_url, request_num, stop_flag, time_out=5):
        StoreWorker.worker_count += 1
        self._id = StoreWorker.worker_count
        threading.Thread.__init__(self,name="store_worker_%d" % self._id)
        self.store_queue = store_queue
        self.page_queue = page_queue
        self.root_url = root_url
        self.time_out = time_out
        self.stop_flag = stop_flag
        self.request_num = request_num
        self.username = username
        self.setDaemon(True)
        self.start()

    def run(self):
        while not self.stop_flag[0]:
            try:
                callback, args = self.store_queue.get(timeout = self.time_out)
                callback(self.getName(),self.username, args)
                # print "stored into database"
                self._is_stop()
            except Queue.Empty:
                pass
                # print "".join([self.getName(),":no task\n"])
            except:
                print "thread %s had some error: %s" % (self.getName(), sys.exc_info()[:2])
        else:
            while not self.store_queue.empty():
                self.store_queue.get()
            print "".join([self.getName(), " finished"])

    def _is_stop(self):
        conn = db_op.db_connect()
        count = db_op.db_get_count(conn, self.root_url, self.username)
        mylock.acquire()
        print "queue size:" + str(self.store_queue.qsize())
        print "count:" + str(count)
        mylock.release()
        if count >= self.request_num or self.page_queue.empty():
            self.stop_flag[0] = True
            db_op.db_update_scan_status(conn, 2, self.username, self.root_url[0])
        db_op.db_close(conn)

class RequestManager(object):
    """ 
        TODO
    """
    def __init__(self, username, worker_num, request_num, is_finished=[False, ]):
        self.page_queue = Queue.Queue()
        self.store_queue = Queue.Queue()
        self.page_workers = []
        self.is_finished = is_finished
        self.store_workers = []
        self.worker_num = worker_num
        self.request_num = request_num
        self.root_url = []
        self.username = username
        self.stop_flag = [False, ]
        self._recruit_threads()

    def _recruit_threads(self):
        for i in range(self.worker_num):
            page_worker = PageWorker(self.page_queue, self.store_queue, self.root_url, self.request_num, self.stop_flag)
            self.page_workers.append(page_worker)
        for i in range(self.worker_num):
            store_worker = StoreWorker(self.page_queue, self.username, self.store_queue, self.root_url, self.request_num, self.stop_flag)
            self.store_workers.append(store_worker)

    def add_job(self, callback, *args):
        self.root_url.append(args[0])
        self.page_queue.put((callback, args))

    def wait_for_complete(self):
        while len(self.page_workers):
            if not self.stop_flag[0]:   
                page_worker = self.page_workers.pop()
                page_worker.join()
                if page_worker.is_alive() and not self.page_queue.empty():
                    self.page_workers.append(page_worker)
            else:
                self.page_workers = []
                break
                
        while len(self.store_workers):
            if not self.stop_flag[0]:
                store_worker = self.store_workers.pop()
                store_worker.join()
                if store_worker.is_alive() and not self.store_queue.empty():
                    self.store_workers.append(store_worker)
            else:
                self.store_workers = []
                break
        self.is_finished[0] = True
        del self
        print "............................................"


if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["root_url=","number=","help", "thread_num="])
    except getopt.GetoptError:
        print "get opt error"
        usage()
    root_url = ""
    request_number = 400
    thread_number = 10
    get_url = False
    for opt in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit(1)
        else:
            if opt[0] == "--root_url":
                get_url = True
                root_url = opt[1]
            if opt[0] == "--number":
                request_number = int(opt[1])
            if opt[0] == "--thread_num":
                thread_number = int(opt[1])
    if get_url:
        tp = RequestManager("loftysoul", worker_num=thread_number, request_num=request_number)
        tp.add_job(deal_page, root_url)
        tp.wait_for_complete()
    else:
        usage()
