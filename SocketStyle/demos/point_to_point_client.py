#!/usr/bin/env python

"""
A simple echo client
"""

import os
import sys

script_path = os.path.realpath(__file__)
script_dir = os.path.dirname(script_path)
parent_dir = os.path.join(script_dir, os.path.pardir)
grandparent_dir = os.path.join(parent_dir, os.path.pardir)
grandparent_dir = os.path.normpath(grandparent_dir)
sys.path.append(grandparent_dir)

import SocketStyle

def main():
    myClient = SocketStyle.PointToPointClient()
    myClient.connect()
    print "Sending data."
    myClient.transmit('Hello world')
    #import time
    #time.sleep(0.1)
    #data = myClient.readall(wait=True)
    data = myClient.read()
    myClient.disconnect()
    print 'Received:',data

if __name__ == "__main__":
    main()
