#!/usr/bin/env python
#-*- coding:utf-8 -*-


from request_collection_manager import RequestManager

class ScanManager(object):
    def __init__(self, thread_num, request_num, root_url,check_types):
        self.root_url = root_url
        self.thread_num = thread_num
        self.request_num = request_num
        self.check_types = check_types
        self.plugin_instances = []

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
        rm = RequestManager(self.thread_num, self.request_num)
        rm.add_job(self.root_url)
        rm.wait_for_complete()
