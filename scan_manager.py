#!/usr/bin/env python
#-*- coding:utf-8 -*-

import time
import threading 
import requests

from request_collection_manager import RequestManager
from util_functions import deal_page
import db_options as do

ISOTIMEFORMAT = '%Y-%m-%d %X'

class ScanManager(object):
    def __init__(self, thread_num, request_num, root_url,check_types, username):
        self.root_url = root_url
        self.request_num = request_num
        if thread_num <20:
            self.thread_num = thread_num
        else:
            self.thread_num = 10
        self.check_types = check_types
        self.plugin_instances = []
        self.username = username
        self.connection_status = self._pre_scan()
        self._store_scan_info()

    def _pre_scan(self):
        res = requests.get(self.root_url)
        if res.status_code == 200:
            self.connection_status = 1
            return 1
        else:
            self.connection_status = -1
            return -1

    def _store_scan_info(self):
        conn = do.db_connect()
        cms = sql = xss = 2
        _check = self.check_types.split(",")[:-1]
        if "sql" in _check:
            sql = 0
        if "cms" in _check:
            cms = 0
        if "xss" in _check:
            xss = 0
        do.db_store_scan_info(conn, (self.username, self.root_url, self.request_num, 
            self.thread_num, self.connection_status, sql, xss, cms,
            time.strftime(ISOTIMEFORMAT, time.localtime()) ))
        do.db_close(conn)

    def _init_plugins(self):
        from plugins_manager import plugins
        for _type in self.check_types:
            if _type in plugins:
                plugin_mod = __import__(_type, fromlist=plugins)
                mod_instance = getattr(plugin_mod, _type)()
                self.plugin_instances.append(mod_instance)

    def check_vun(self):
        self._init_plugins()

    def do_scan(self):
        if self.connection_status == 1:
            rm = RequestManager(self.username, self.thread_num, self.request_num)
            rm.add_job(deal_page, self.root_url)
            t = threading.Thread(target=rm.wait_for_complete)
            t.start()

