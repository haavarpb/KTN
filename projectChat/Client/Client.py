# -*- coding: utf-8 -*-
import socket
from MessageReceiver import MessageReceiver
import sys
import json

class Client:
    """
    This is the chat client class
    """

    def __init__(self, host, server_port):
        """
        This method is run when creating a new Client object
        """

        # Set up the socket connection to the server
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.server_port = server_port
        self.run()

    def run(self):
        # Initiate the connection to the server
        self.connection.connect((self.host, self.server_port))

        while True:
            data = raw_input("-------------------------------------------------------\n::")
            if data == 'exit':
                self.disconnect()
                sys.exit()

            self.send_payload(str(data))

        
    def disconnect(self):
        self.send_payload(json.dumps({'request':'logout', 'content': None}))
        self.connection.shutdown()
        self.connection.close()

    def send_payload(self, data):
        splitted = data.split(" ")
        if len(splitted) == 2:
            self.connection.sendall(json.dumps({'request': splitted[0], 'content':splitted[1]}))
        else:
            self.connection.sendall(json.dumps({'request': 'msg', 'content':data}))

        
    


if __name__ == '__main__':
    """
    This is the main method and is executed when you type "python Client.py"
    in your terminal.

    No alterations are necessary
    """
    client = Client('localhost', 9998)
