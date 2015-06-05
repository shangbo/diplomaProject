#!/usr/bin/env python
# -*- coding:utf-8 -*-
import cPickle as pkl
import requests
from bs4 import BeautifulSoup as bs

def get_para_keys(item):
    paras = pkl.loads(item[6].encode("utf-8"))
    keys = []
    for p in paras:
        keys.append(p[0])
    return keys


def run(thread_name, item):
    keys = get_para_keys(item)
    pocs = ["<script>alert('%s')</script>", ]
    injectable_log = ""
    injectable_point = []
    for key in keys:
        injectable_pocs = []
        for pre_poc in pocs:
            poc = pre_poc % key
            if item[4] == "GET":
                url = item[5] + "?" + key + "=" + poc
                response = requests.get(url)
                content = response.content
                html = bs(content)
                scripts = html.findAll("script")
                for s in scripts:
                    if s.getText() == "alert('%s')" % key:
                        injectable_pocs.append(poc)
            else:
                pass
        if injectable_pocs:
            injectable_point.append(key)
            injectable_log += str(key + ":" + str(injectable_pocs) + "\n")
        else:
            injectable_log += str(key + "No bugs\n")
    return [len(injectable_point), "Normal", injectable_log, injectable_point]

