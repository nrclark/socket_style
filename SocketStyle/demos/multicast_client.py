#!/usr/bin/env python

import sys
import os
import time

script_path = os.path.realpath(__file__)
script_dir = os.path.dirname(script_path)
parent_dir = os.path.join(script_dir, os.path.pardir)
grandparent_dir = os.path.join(parent_dir, os.path.pardir)
grandparent_dir = os.path.normpath(grandparent_dir)
sys.path.append(grandparent_dir)

import SocketStyle


def main():
    myRx = SocketStyle.MulticastClient()
    myRx.open()
    count = 0
    while 1:
        try:
            if myRx.has_data():
                print myRx.read()
            time.sleep(0.05)

        except KeyboardInterrupt:
            count += 1
            myRx.close()
            if count == 3:
                sys.exit(0)
            myRx.open()

if __name__ == '__main__':
    main()
