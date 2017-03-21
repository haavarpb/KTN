# -*- coding: utf-8 -*-
from threading import Thread
import json

class MessageReceiver(Thread):
    """
    This is the message receiver class. 
    The class inherits Thread, something that
    is necessary to make the MessageReceiver start a new thread, and it allows
    the chat client to both send and receive messages at the same time
    """

    def __init__(self, client, connection):
        """
        This method is executed when creating a new MessageReceiver object
        """
        super(MessageReceiver,self).__init__()
        # Flag to run thread as a deamon
        self.daemon = True
        self.client = client
        self.connection = connection

    def run(self):
        while True:
            s = self.connection.recv(4096)
            r = json.loads(s)

            if r['response'] == 'info' and isinstance(r['content'], list):
                    dList = r['content']
                    for d in dList:
                        print '[Server info] ' + d
            elif r['response'] == 'history':
                print '[Server Log] ' + '[' + r['content']['sender'] + '@' + r['content']['timestamp'] + '] ' + r['content']['content']
            elif r['response'] == 'message':
                print '[' + r['sender'] + '@' + r['timestamp'] + '] ' + r['content'] + "\n"
            elif r['response'] == 'error':
                print '[Server error] ' + r['content'] + "\n"
            elif r['response'] == 'info':
                print '[Server info] ' + r['content'] + "\n"