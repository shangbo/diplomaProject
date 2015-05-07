#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import Flask, render_template
from flask.ext.socketio import SocketIO, send, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@socketio.on('message')
def handle_message(message):
    send("123")


if __name__ == '__main__':
    socketio.run(app)