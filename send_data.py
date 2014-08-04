#!/usr/bin/env python

"""
A simple echo client
"""

import os
import sys

import SocketStyle

def main():
    myClient = SocketStyle.PointToPointClient()
    myClient.connect()
    myClient.transmit('Hello world')
    myClient.disconnect()

if __name__ == "__main__":
    main()
