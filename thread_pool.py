#!/usr/bin/env python
#-*- coding:utf-8 -*-

class ThreadPool(object):
    
    def __init__(self, username, worker_num, request_num):
        self.worker_num = worker_num