#!/usr/bin/env python
#-*- coding:utf-8 -*-

import time
import threading 
import requests

from request_collection_manager import RequestManager
from util_functions import deal_page
import db_options as do
from plugins_manager import PluginsManager

ISOTIMEFORMAT = '%Y-%m-%d %X'


class ScanManager(object):
    def __init__(self, thread_num, request_num, root_url, check_types, username):
        self.root_url = root_url
        self.request_num = request_num
        if thread_num < 20:
            self.thread_num = thread_num
        else:
            self.thread_num = 10
        self.check_types = check_types
        self.plugin_instances = []
        self.username = username
        self.scan_finished = [False, ]
        self.connection_status = self._pre_scan()
        if self.connection_status == 2:
            self._store_scan_info()

    def _pre_scan(self):
        try:
            res = requests.get(self.root_url)
            if res.status_code == 200:
                self.connection_status = 2
                return 2
            else:
                self.connection_status = -1
                return -1
        except requests.ConnectionError:
            return -2

    def _store_scan_info(self):
        conn = do.db_connect()
        _check = self.check_types.split(",")[:-1]

        do.db_clear_repeat_scan(conn, self.username, self.root_url) 
        do.db_move_to_history(conn, self.username, self.root_url)
        scan_info = (self.username, self.root_url, self.request_num, 
                     self.thread_num, self.connection_status, self.check_types,
                     time.strftime(ISOTIMEFORMAT, time.localtime()))
        do.db_store_scan_info(conn, scan_info)
        for c in _check:
            do.db_modify_table_structure(conn, c)
    
        do.db_close(conn)

    def check_vun(self):
        t = threading.Thread(target=self._check_vun_thread)
        t.start()

    def _check_vun_thread(self):
        if self.connection_status == 2:
            while not self.scan_finished[0]:
                time.sleep(1)

            if self.scan_finished[0]:
                pm = PluginsManager(self.thread_num, self.root_url, self.username, self.check_types)
                t = threading.Thread(target=pm.wait_for_complete)
                t.start()

    def do_scan(self):
        if self.connection_status == 2:
            conn = do.db_connect()
            rm = RequestManager(self.username, self.thread_num, self.request_num, self.scan_finished)
            rm.add_job(deal_page, self.root_url)
            do.db_update_scan_status(conn, 1, self.username, self.root_url)
            do.db_close(conn)
            t = threading.Thread(target=rm.wait_for_complete)
            t.start()

