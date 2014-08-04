#!/usr/bin/env python

"""
Various socket designs.
"""
import socket
import struct
import select


class MulticastServer:
    """Provides a simple UDP-based multicast transmitter."""
    def __init__(self, multicast_address='224.0.0.1',
                 multicast_port=10000, ttl=1):
        """Creates a new socket-based multicast transmitter.

        :param multicast_address: Target multicast group address.
        :param multicast_port: Target multicast port.
        :param ttl: Multicast TTL. Increase to allow network multicasting.
        """
        self._multicast_address = multicast_address
        self._multicast_port = multicast_port
        self._ttl = ttl
        self.sock = None
        self.isOpen = False
        self.multicast = (self._multicast_address, self._multicast_port)

    def open(self):
        """Opens the multicast socket for writing."""

        if self.isOpen:
            return

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except AttributeError:
            pass

        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL,  struct.pack('=b', self._ttl))
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, struct.pack('=b', 1))
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF,   socket.inet_aton("127.0.0.1"))         

        self.isOpen = True

    def transmit(self, data):
        """Transmits a block of data using socket.sendto(). Retries until
        the entire chunk is transmitted.

        :param data: Message to transmit.
        :type data: string
        """
        assert self.isOpen
        size = len(data)
        sent = 0
        while sent != size:
            sent += self.sock.sendto(data[sent:], self.multicast)

    def close(self):
        """Closes the socket."""
        if not self.isOpen:
            return
        self.sock.close()
        self.isOpen = False


class MulticastClient:
    """Provides a simple UDP-based multicast receiver."""
    def __init__(self, multicast_address='224.0.0.1',
                 multicast_port=10000):
        """Creates a new socket-based multicast receiver.

        :param multicast_address: Target multicast group address.
        :param multicast_port: Target multicast port.
        """
        self._maxReceive = 4096
        self._multicast_address = multicast_address
        self._multicast_port = multicast_port
        self.sock = None
        self.isOpen = False
        self.multicast = (self._multicast_address, self._multicast_port)

    def open(self):
        """Opens the multicast socket for receiving."""
        if self.isOpen:
            return

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                                  socket.IPPROTO_UDP)
        
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except AttributeError:
            pass
        
        self.sock.bind(self.multicast)
        mreq = struct.pack("4sl", socket.inet_aton(self._multicast_address),
                           socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self.isOpen = True

    def has_data(self):
        """Checks for the presence of waiting messages."""
        ready_items = select.select([self.sock], [], [], 0)[0]
        if len(ready_items) == 0:
            return False
        else:
            return True

    def wait_for_packet(self, timeout=None):
        """Blocks until a packet is available.

        :param timeout: Maximum time to wait for a packet, in seconds. \
                        A value of None will wait indefinitely.
        :type timeout: Integer, float, or None.
        """
        if timeout is None:
            select.select([self.sock], [], [])
        else:
            timeout = float(timeout)
            select.select([self.sock], [], [], timeout)

    def read(self):
        """Returns a message from the queue."""
        assert self.isOpen
        return self.sock.recv(self._maxReceive)

    def close(self):
        """Closes the socket."""
        if not self.isOpen:
            return
        self.sock.close()
        self.isOpen = False





