#!/usr/bin/env python3
"""NMK heartbeat — يحدّث LastAthenaPingTime باستمرار لإظهار الجهاز كمتصل"""
import time
import socket
from openpilot.common.params import Params

def has_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def main():
    p = Params()
    while True:
        if has_internet():
            p.put("LastAthenaPingTime", int(time.time() * 1e9))
        time.sleep(30)

if __name__ == "__main__":
    main()
