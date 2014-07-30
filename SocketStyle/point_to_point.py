#!/usr/bin/env python

"""
Various socket designs.
"""
import socket
import struct
import select

from socketstyle_common import TimeoutError

class PointToPointServer:
    def __init__(self, host="127.0.0.1", port=50000):
        """Initializes an instance of PointToPointServer with
        various default values.
        :param host: Host IP to listen on.
        :param port: Host port to listen on.
        """
        self._host = host
        self._port = port
        self._maxReceive = 4096
        self._backlog = 5
        self.sock = None
        self.client = None
        self.isOpen = False
        self.isConnected = False
        self.timeout = None

    def open(self):
        """Opens a socket for listening. Connections to clients still need
        to be made by connect() before anything will work."""

        if self.isOpen:
            return

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self._host, self._port))
        self.sock.listen(self._backlog)
        self.isOpen = True

    def connect(self, timeout='default'):
        """Opens a socket for listening. Connections to clients still need
        to be made by connect() before anything will work."""

        assert self.isOpen
        if self.isConnected:
            return

        if type(timeout) == str:
            if timeout.lower().strip() == 'default':
                timeout = self.timeout

            elif timeout.lower().strip() == 'none':
                timeout = self.timeout

            else:
                timeout = float(timeout)

        self.sock.settimeout(timeout)

        try:
            self.client = self.sock.accept()[0]
        except Exception as e:
            self.sock.settimeout(self.timeout)
            if e == socket.timeout:
                raise TimeoutError("Timed out waiting for a client connection.")
            else:
                raise e

        self.sock.settimeout(self.timeout)
        self.isConnected = True
        return True

    def has_data(self):
        """Checks for data waiting in the receiver queue."""
        assert self.isOpen
        assert self.isConnected
        ready_items = select.select([self.client], [], [self.client], 0)

        if len(ready_items[2]) != 0:
            raise IOError, "Exception checking for data."

        if len(ready_items[0]) != 0:
            return True

        return False

    def wait_for_packet(self, timeout=None):
        """Blocks until a packet is available."""
        assert self.isOpen
        assert self.isConnected
        if timeout is None:
            result = select.select([self.client], [], [self.client])
        else:
            timeout = float(timeout)
            result = select.select([self.client], [], [self.client], timeout)

    def read(self):
        """Reads a packet from the receive buffer."""
        assert self.isOpen
        assert self.isConnected
        return self.client.recv(self._maxReceive)

    def readall(self, wait=False, timeout=None):
        """Returns all currently pending data in the receive buffer."""
        assert self.isOpen
        assert self.isConnected
        if wait:
            self.wait_for_packet(timeout)
        chunks = []
        chunk = None

        while chunk != '' and self.has_data():
            chunk = self.client.recv(self._maxReceive)
            chunks.append(chunk)

        return ''.join(chunks)

    def transmit(self, data):
        """Transmits a block of data."""
        assert self.isOpen
        assert self.isConnected

        size = len(data)
        sent = 0
        while sent != size:
            sent += self.client.send(data[sent:])

    def disconnect(self):
        """Disconnects the client socket."""
        if not self.isConnected:
            return
        try:
            self.client.shutdown(socket.SHUT_RDWR)
        except socket.error:
            pass
        self.client.close()
        self.isConnected = False

    def close(self):
        """Closes the server socket."""
        if not self.isOpen:
            return
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except socket.error:
            pass
        self.sock.close()
        self.isOpen = False


class PointToPointClient:
    def __init__(self, host="127.0.0.1", port=50000):
        self._host = host
        self._port = port
        self._maxReceive = 4096
        self.sock = None
        self.isConnected = False
        self.timeout = None

    def connect(self, timeout='default'):
        """Connects to a server socket."""
        if self.isConnected:
            return

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if type(timeout) == str:
            if timeout.lower().strip() == 'default':
                timeout = self.timeout

            elif timeout.lower().strip() == 'none':
                timeout = self.timeout

            else:
                timeout = float(timeout)

        self.sock.settimeout(timeout)

        try:
            self.sock.connect((self._host, self._port))
        except Exception as e:
            self.sock.settimeout(self.timeout)
            if e == socket.timeout:
                raise TimeoutError("Timed out waiting for a server connection.")
            else:
                raise e

        self.sock.settimeout(self.timeout)
        self.isConnected = True

    def has_data(self):
        """Checks for data waiting in the receiver queue."""
        ready_items = select.select([self.sock], [], [self.sock], 0)

        if len(ready_items[2]) != 0:
            raise IOError, "Exception checking for data."

        if len(ready_items[0]) != 0:
            return True

        return False

    def wait_for_packet(self, timeout=None):
        """Blocks until a packet is available."""
        if timeout is None:
            result = select.select([self.sock], [], [self.sock])
        else:
            timeout = float(timeout)
            result = select.select([self.sock], [], [self.sock], timeout)

    def read(self):
        """Reads a single block of data from the receiver queue."""
        assert self.isConnected
        return self.sock.recv(self._maxReceive)

    def readall(self, wait=False, timeout=None):
        """Returns all currently pending data in the receive buffer."""
        assert self.isConnected
        if wait:
            self.wait_for_packet(timeout)

        chunks = []
        chunk = None

        while chunk != '':
            chunk = self.sock.recv(self._maxReceive)
            chunks.append(chunk)

        return ''.join(chunks)

    def transmit(self, data):
        """Transmits a packet to the server."""
        assert self.isConnected
        self.sock.send(data)

    def disconnect(self):
        """Disconnects from the server."""
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except socket.error:
            pass
        self.sock.close()
        self.isConnected = False


def main():
    return


if __name__ == '__main__':
    main()






