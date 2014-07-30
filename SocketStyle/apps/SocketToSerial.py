#!/usr/bin/env python

__author__ = 'nrclark'

import threading
import traceback
import serial
import sys
import time

sys.path.append("/Users/nrclark/PycharmProjects/SocketStyle")

import SocketStyle


def _safe_runner(function, *args, **kwargs):
    return_code = None
    try:
        return_code = function(*args, **kwargs)
    except:
        traceback.print_exc(file=sys.stderr)

    return return_code


class SerialTransmitterThread(threading.Thread):
    def __init__(self, mySerial=None, stopRequest=None, max_interval=0.1):
        threading.Thread.__init__(self)

        self.max_interval = float(max_interval)

        self.stopEvent = threading.Event()
        self.stopEvent.clear()

        if stopRequest is None:
            self.stopRequest = threading.Event()
            self.stopRequest.clear()
        else:
            self.stopRequest = stopRequest

        self.mySerial = mySerial
        self.myServer = SocketStyle.PointToPointServer()
        self.myServer.open()

    def run(self):
        self.myServer.open()
        self.mySerial.writeTimeout = self.max_interval
        error = None

        try:
            while True:
                connected = False
                try:
                    self.myServer.connect(self.max_interval)
                    connected = True
                except SocketStyle.TimeoutError:
                    pass

                if self.stopRequest.isSet():
                    break

                if connected:
                    data = self.myServer.readall()
                    self.myServer.disconnect()
                    self.mySerial.write(data)
        except Exception as e:
            error = e

        _safe_runner(self.mySerial.flush)
        _safe_runner(self.myServer.disconnect)
        _safe_runner(self.myServer.close)
        self.stopEvent.set()

        if error is not None:
            raise error


class SerialReceiverThread(threading.Thread):
    def __init__(self, mySerial=None, stopRequest=None, timeout_interval=0.1):
        threading.Thread.__init__(self)

        self.timeout_interval = float(timeout_interval)

        self.stopEvent = threading.Event()
        self.stopEvent.clear()

        if stopRequest is None:
            self.stopRequest = threading.Event()
            self.stopRequest.clear()
        else:
            self.stopRequest = stopRequest

        self.mySerial = mySerial
        self.myServer = SocketStyle.MulticastServer()

    def run(self):
        self.myServer.open()
        self.mySerial.timeout = self.timeout_interval
        error = None

        try:
            while True:
                data = self.mySerial.read(1)
                if len(data) != 0:
                    available = self.mySerial.inWaiting()

                    if available:
                        data += self.mySerial.read(available)
                    self.myServer.transmit(data)
        except Exception as e:
            error = e

        _safe_runner(self.myServer.close)
        self.stopEvent.set()

        if error is not None:
            raise error


def main():
    master_kill = threading.Event()
    mySerial = serial.Serial(baudrate=115200, parity='N')
    transmitter_thread = SerialTransmitterThread(mySerial, master_kill)
    receiver_thread = SerialReceiverThread(mySerial, master_kill)

    transmitter_death = transmitter_thread.stopEvent
    receiver_death = receiver_thread.stopEvent
    error = None

    try:
        transmitter_thread.start()
        receiver_thread.start()
    except Exception as e:
        master_kill.set()
        error = e

    if error is None:
        try:
            while True:
                if not transmitter_thread.isAlive():
                    master_kill.set()
                    break
                if not receiver_thread.isAlive():
                    master_kill.set()
                    break

                time.sleep(0.1)

        except Exception as e:
            master_kill.set()
            error = e

    counts = 0
    while transmitter_thread.isAlive() or receiver_thread.isAlive():
        time.sleep(1)
        print counts, transmitter_thread.isAlive(), receiver_thread.isAlive()
        counts += 1
        if counts == 20:
            break

    if error is not None:
        raise error


if __name__ == "__main__":
    main()
