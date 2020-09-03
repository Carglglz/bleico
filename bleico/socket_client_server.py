#!/usr/bin/env python3
"""
Copyright (c) 2020 Carlos G. Gonzalez and others (see the AUTHORS file).
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

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

    def __init__(self, port, buff=1024, log=None):

        self.host = 'localhost'
        self.port = port
        self.serv_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serv_soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.addr = None
        self.buff = bytearray(buff)
        self.conn = None
        self.addr_client = None
        self.log = log

    def get_free_port(self):
        while True:
            try:
                self.serv_soc.bind((self.host, self.port))
                break
            except Exception as e:
                self.port += 1
        return self.port

    def start_SOC(self):
        self.serv_soc.listen(1)
        self.log.info('Notification Server listening...')
        self.conn, self.addr_client = self.serv_soc.accept()
        self.log.info('Connection received from [NotifyThread]: {}'.format(self.addr_client))
        self.conn.settimeout(10)

    def send_message(self, message):
        self.conn.sendall(bytes(message, 'utf-8'))

    def recv_message(self):
        self.buff[:] = self.conn.recv(len(self.buff))
        return self.buff.decode()
