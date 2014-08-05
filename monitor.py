#!/usr/bin/env python

import sys
import signal
import time
import SocketStyle

class MonitorApp:
    def __init__(self):
        self.client = SocketStyle.MulticastClient()
        self.client.open()
        signal.signal(signal.SIGINT,  self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        self.stop = False

    def _signal_handler(self, signal, frame):
        self.close()
    
    def close(self):
        self.stop = True

    def loop(self):
        while 1:
            if self.stop:
                break
                
            if self.client.has_data():
                data = self.client.read()
                sys.stdout.write(data)
                sys.stdout.flush()
            else:
                time.sleep(0.05)

def main():
    app = MonitorApp()
    app.loop()

if __name__ == '__main__':
    main()
