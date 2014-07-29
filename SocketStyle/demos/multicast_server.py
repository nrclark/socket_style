#!/usr/bin/env python

"""
A simple echo server multicast
"""
import sys
import time
import os

script_path = os.path.realpath(__file__)
script_dir = os.path.dirname(script_path)
parent_dir = os.path.join(script_dir, os.path.pardir)
grandparent_dir = os.path.join(parent_dir, os.path.pardir)
grandparent_dir = os.path.normpath(grandparent_dir)
sys.path.append(grandparent_dir)

import SocketStyle


def main():
    myTx = SocketStyle.MulticastServer()
    myTx.open()
    x = 0
    count = 0
    while 1:
        try:
            x += 1
            print "Sending %d to clients"%x
            myTx.transmit("Server says #%d"%x)
            time.sleep(1)

        except KeyboardInterrupt:
            count += 1
            myTx.close()
            if count == 3:
                sys.exit(0)
            myTx.open()

if __name__ == '__main__':
    main()






