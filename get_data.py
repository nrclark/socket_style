#!/usr/bin/env python

import sys
import os

import SocketStyle

def main():
    myRx = SocketStyle.MulticastClient()
    myRx.open()

    while 1:
        try:
            myRx.wait_for_packet()
            sys.stdout.write(myRx.read())

        except KeyboardInterrupt:
            myRx.close()
            sys.exit(0)

if __name__ == '__main__':
    main()
