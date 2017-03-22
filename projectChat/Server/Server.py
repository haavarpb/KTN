# -*- coding: utf-8 -*-
import SocketServer
from threading import Lock
import json
import time


class ClientHandler(SocketServer.BaseRequestHandler):
    """
    This is the ClientHandler class. Everytime a new client connects to the
    server, a new ClientHandler object will be created. This class represents
    only connected clients, and not the server itself. If you want to write
    logic for the server, you must write it outside this class
    """

    def handle(self):
        """
        This method handles the connection between a client and the server.
        """
        self.ip = self.client_address[0]
        self.port = self.client_address[1]
        self.connection = self.request
        self.username = None

        # Loop that listens for messages from the client
        while True:
            received_string = self.connection.recv(4096)
            received_dict = json.loads(received_string)
            req = received_dict['request']
            try:
                content = received_dict['content']
            except:
                content = None

            if self.server.isLoggedIn(self):
                if req == 'logout':
                    self.logout(self.username)
                    break
                elif req == 'msg':
                    self.message(content, self.username)
                    continue
                elif req == 'names':
                    responses = self.names()
                elif req == 'history':
                    responses = self.history()
                elif req == 'help':
                    responses = self.help()
                else:
                    responses = self.error('Invalid message. Type <help> to learn more.')
            else:
                if req == 'login':
                    if self.isValidUsername(content):
                        if self.server.isUserNameTaken(content):
                            responses = self.error('Username taken. Try again.')
                        else:
                            responses = self.login(content)
                            self.username = content
                    else:
                        responses = self.error('Invalid username. Try again.')
                elif req == 'help':
                    responses = self.help()
                else:
                    responses = self.error(
                        'Access denied. You are not logged in. Type <help> to learn more.'
                    )

            for response in responses:
                payload = json.dumps(response)
                self.connection.sendall(payload)
                time.sleep(0.1)


    def login(self, username):
        self.server.addClient(self, username)
        return [self.response('server', 'info', 'Login success.')]

    def isValidUsername(self, username):
        for character in username:
            if character not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmonpqrstuvwxyz1234567890":
                return False
        return True

    def logout(self, username):
        self.server.deleteClient(self, username)

    def message(self, message, username):
        response = self.response(username, 'message', message)
        self.logger(json.dumps(response))
        self.server.broadcast(json.dumps(response))

    def names(self):
        return [self.response('server', 'info', self.server.getNames(self))]

    def history(self):
        return [self.response('server','history', self.server.getServerHistory())]
        

    def help(self):
        message = "Chat commands:\n"\
        "To log in:                                                  login <username>\n"\
        "To log out (Requires login):                                logout <None>\n"\
        "To get server message-history type (Requires login):        history <None>\n"\
        "To get a list of logged in users type (Requires login):     names <None> \n"\
        "To show this list of availible commands again type:         help <None>\n"
        return [self.response('server', 'info', message)]

    def error(self, message):
        return [self.response('server', 'error', message)]

    def timestampAsString(self):
        return str(time.localtime()[3]) + ":" + str(time.localtime()[4]) + ("AM" if time.localtime()[3] < 12 else "PM")

    def response(self, sender, response, content):
        return {
                'timestamp':self.timestampAsString(),
                'sender':sender,
                'response':response,
                'content': content
                }

    def logger(self, jsonMessage):
        self.server.fileLock.acquire()
        f = open(self.server.file, "a")
        f.write(jsonMessage + "\n")
        f.close()
        self.server.fileLock.release()




class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    connectedClients = {}
    connectedClientsLock = Lock()

    file = "history.txt"
    fileLock = Lock()

    allow_reuse_address = True


    def addClient(self, client, username):
        self.broadcast(json.dumps(client.response('server', 'message', username + ' logged in.')))
        self.connectedClientsLock.acquire()
        self.connectedClients[client] = username
        self.connectedClientsLock.release()

    def deleteClient(self, client, username):
        self.connectedClientsLock.acquire()
        del self.connectedClients[client]
        self.connectedClientsLock.release()
        self.broadcast(json.dumps(client.response('server', 'message', username + ' logged out.')))
        self.shutdown_request(client.request)
        self.close_request(client.request)

    def isUserNameTaken(self, username):
        self.connectedClientsLock.acquire()
        if username in self.connectedClients.values():
            self.connectedClientsLock.release()
            return True
        else:
            self.connectedClientsLock.release()
            return False

    def isLoggedIn(self, client):
        self.connectedClientsLock.acquire()
        if client not in self.connectedClients.keys():
            self.connectedClientsLock.release()
            return False
        self.connectedClientsLock.release()
        return True

    def getNames(self, client):
        # Array with names
        return self.connectedClients.values()

    def broadcast(self, message):
        self.connectedClientsLock.acquire()
        for client in self.connectedClients.keys():
            client.connection.sendall(message)
        self.connectedClientsLock.release()

    def getServerHistory(self):
        messageHistory = []
        self.fileLock.acquire()
        f = open(self.file, "r")
        for line in f:
            messageHistory.append(json.loads(line.strip("\n")))
        self.fileLock.release()
        return messageHistory


if __name__ == "__main__":
    """
    This is the main method and is executed when you type "python Server.py"
    in your terminal.

    No alterations are necessary
    """
    HOST, PORT = 'localhost', 9998
    print 'Server running...'

    # Set up and initiate the TCP server
    server = ThreadedTCPServer((HOST, PORT), ClientHandler)
    server.serve_forever()
