#!/usr/bin/env python

import sys
import os
import time
import SocketStyle

def main():
    myRx = SocketStyle.MulticastClient()
    myRx.open()

    try:
        while 1:
            if myRx.has_data():
                data = myRx.read()            
                sys.stdout.write(data)
                sys.stdout.flush()
            else:
                time.sleep(0.05)

                        #myRx.wait_for_packet()
            

    except KeyboardInterrupt:
        myRx.close()
        sys.exit(0)

if __name__ == '__main__':
    main()
