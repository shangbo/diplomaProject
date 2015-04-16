#!/usr/bin/env python
# -*- coding:utf-8 -*-

#third-party web frame lib
from flask import Flask, render_template, request

#custom lib
import db_options as do
from thread_pool import ThreadPool, deal_page

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("submit_page.html")

@app.route("/submit_form.html", methods=["POST"])
def submit_form():
    if request.method == "POST":
        url = request.form["url_string"]
        email = request.form["email_string"]
        request_number = request.form["request_num"]
        thread_number = request.form["thread_num"]
        if request_number:
            request_number = int(request_number)
        else:
            request_number = 400            
        if thread_number:
            thread_number = int(thread_number)
        else:
            thread_number = 10
        print url
        print email
        print request_number
        print thread_number
        pool = ThreadPool(worker_num=thread_number, request_num=request_number)
        pool.add_job(deal_page, url)
    return render_template("successful.html")
if __name__ == "__main__":
    
    app.run(debug=True)