#!/usr/bin/env python

__author__ = 'nrclark'

import threading
import traceback
import serial
import sys
import time
import signal
import SocketStyle
import ConfigParser

def safe_runner(function, *args, **kwargs):
    return_code = None
    try:
        return_code = function(*args, **kwargs)
    except:
        traceback.print_exc(file=sys.stderr)

    return return_code

def match_section(config, section):
    names = [x.lower().strip() for x in config.sections()]
    index = names.index(section.lower().strip())
    return config.sections()[index]

class SerialTransmitterThread(threading.Thread):
    def __init__(self, config=None, device_name=None, mySerial=None,
                 stopRequest=None, max_interval=0.1):
        
        threading.Thread.__init__(self)

        self.max_interval = float(max_interval)

        self.stopEvent = threading.Event()
        self.stopEvent.clear()

        if stopRequest is None:
            self.stopRequest = threading.Event()
            self.stopRequest.clear()
        else:
            self.stopRequest = stopRequest

        host_ip = config.get(device_name, 'host_ip').strip()
        ttl = config.getint(device_name, 'ttl')
        tx_port = config.getint(device_name, 'tx_port')
        
        self.mySerial = mySerial
        self.myServer = SocketStyle.PointToPointServer(
            host = host_ip, 
            port = tx_port, 
            ttl = ttl
        )
        
        self.myServer.open()

    def run(self):
        self.myServer.open()
        self.mySerial.writeTimeout = self.max_interval
        error = None

        try:
            while True:
                if self.stopRequest.isSet():
                    break

                connected = False
                try:
                    self.myServer.connect(self.max_interval)
                    connected = True
                except SocketStyle.TimeoutError:
                    pass

                if connected:
                    data = self.myServer.readall(wait=True, timeout=2)
                    self.myServer.disconnect()
                    self.mySerial.write(data)

        except Exception as e:
            error = e

        safe_runner(self.mySerial.flush)
        safe_runner(self.myServer.disconnect)
        safe_runner(self.myServer.close)
        self.stopEvent.set()

        if error is not None:
            raise error


class SerialReceiverThread(threading.Thread):
    def __init__(self, config=None, device_name=None, 
                 mySerial=None, stopRequest=None, max_interval=0.1):
        threading.Thread.__init__(self)

        self.timeout_interval = float(max_interval)

        self.stopEvent = threading.Event()
        self.stopEvent.clear()

        if stopRequest is None:
            self.stopRequest = threading.Event()
            self.stopRequest.clear()
        else:
            self.stopRequest = stopRequest

        multicast_address = config.get(device_name, 'rx_multicast_address')
        multicast_port = config.getint(device_name, 'rx_multicast_port')
        ttl = config.getint(device_name, 'ttl')
        host_ip = config.get(device_name, 'host_ip')

        multicast_address = multicast_address.strip()
        host_ip = host_ip.strip()
        
        self.mySerial = mySerial

        self.myServer = SocketStyle.MulticastServer(
            multicast_address=multicast_address,
            multicast_port=multicast_port,
            ttl=ttl,
            multicast_interface=host_ip)


    def run(self):
        self.myServer.open()
        self.mySerial.timeout = self.timeout_interval
        error = None

        try:
            while True:
                if self.stopRequest.isSet():
                    break
                                
                data = self.mySerial.read(1)
                if len(data) != 0:
                    available = self.mySerial.inWaiting()

                    if available:
                        data += self.mySerial.read(available)
                    
                    self.myServer.transmit(data)
        
        except Exception as e:
            error = e

        safe_runner(self.myServer.close)
        self.stopEvent.set()

        if error is not None:
            raise error

class MonitorApp:
    def __init__(self, config, device_name = 'primary'):        
        self.master_kill = threading.Event()
                
        port = config.get(device_name, 'port').strip()
        baudrate = config.getint(device_name, 'baudrate')
        parity = config.get(device_name, 'parity')
        parity = parity.strip()[0].upper()
        
        self.mySerial = serial.Serial(
            port = port,
            baudrate = baudrate,
            parity = parity
        )        

        self.mySerial.flushInput()
        self.mySerial.flushOutput()

        self.tx_thread = SerialTransmitterThread (
            config = config,
            device_name = device_name,
            mySerial = self.mySerial,
            stopRequest = self.master_kill, 
            max_interval = 0.05
        )
        
        self.rx_thread = SerialReceiverThread (
            config = config,
            device_name = device_name,
            mySerial = self.mySerial,
            stopRequest = self.master_kill, 
            max_interval = 0.05
        )

        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signal, frame):
        self.shutdown()

    def shutdown(self):
        self.master_kill.set()
        
        for x in range(200):
            if self.tx_thread.isAlive() or self.rx_thread.isAlive():
                time.sleep(0.1)
            else:
                safe_runner(self.mySerial.close)
                return
        else:
            safe_runner(self.mySerial.close)
            raise threading.ThreadError,"Couldn't stop threads."

    def run(self):
        error = None
        try:
            self.tx_thread.start()
            self.rx_thread.start()
        
        except Exception as e:
            self.master_kill.set()
            error = e

        if error is None:
            try:
                while True:
                    if not self.tx_thread.isAlive():
                        self.master_kill.set()
                        break
                    if not self.rx_thread.isAlive():
                        self.master_kill.set()
                        break

                    time.sleep(0.1)

            except Exception as e:
                self.master_kill.set()
                error = e

        self.shutdown()
        if error is not None:
            raise error


def main():
    config = ConfigParser.ConfigParser()
    config.read('config.ini')
    device_name = match_section(config, 'primary')
                
    try:
        myApp = MonitorApp(config, device_name)

    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
    
    except Exception as e:
        sys.stderr.write(str(e)+'\n')
        sys.exit(1)
    
    myApp.run()

if __name__ == "__main__":
    main()
