#!/usr/bin/env python
# @Author: carlosgilgonzalez
# @Date:   2019-07-25T02:38:19+01:00
# @Last modified by:   carlosgilgonzalez
# @Last modified time: 2019-07-25T22:52:04+01:00


import socket


class socket_client:
    """
    Socket client simple class
    """

    def __init__(self, port, buff=1024):
        self.cli_soc = None
        self.host = 'localhost'
        self.port = port
        self.cli_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cli_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.addr = (self.host, self.port)
        self.buff = bytearray(buff)

    def connect_SOC(self):
        self.cli_soc.connect(self.addr)
        # self.cli_soc.settimeout(0.01)

    def send_message(self, message):
        self.cli_soc.sendall(bytes(message, 'utf-8'))

    def recv_message(self):

        self.buff[:] = self.cli_soc.recv(len(self.buff))
        return self.buff.decode()


class socket_server:
    """
    Socket server simple class
    """

    def __init__(self, port, buff=1024):

        self.host = 'localhost'
        self.port = port
        self.serv_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serv_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.addr = None
        self.buff = bytearray(buff)
        self.conn = None
        self.addr_client = None

    def start_SOC(self):
        self.serv_soc.bind((self.host, self.port))
        self.serv_soc.listen(1)
        print('Server listening...')
        self.conn, self.addr_client = self.serv_soc.accept()
        print('Connection received...')
        print(self.addr_client)
        # self.conn.settimeout(1)

    def send_message(self, message):
        self.conn.sendall(bytes(message, 'utf-8'))

    def recv_message(self):
        self.buff[:] = self.conn.recv(len(self.buff))
        return self.buff.decode()
