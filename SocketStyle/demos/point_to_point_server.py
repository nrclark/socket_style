#!/usr/bin/env python

"""
A simple echo server
"""

import os
import sys
import time

script_path = os.path.realpath(__file__)
script_dir = os.path.dirname(script_path)
parent_dir = os.path.join(script_dir, os.path.pardir)
grandparent_dir = os.path.join(parent_dir, os.path.pardir)
grandparent_dir = os.path.normpath(grandparent_dir)
sys.path.append(grandparent_dir)

import SocketStyle


def main():
    myServer = SocketStyle.PointToPointServer()
    myServer.open()

    while True:
        myServer.connect()
        import time
        time.sleep(0.1)
        data = myServer.readall()
        print "got:",data
        myServer.transmit(data)
        myServer.disconnect()

if __name__ == "__main__":
    main()
