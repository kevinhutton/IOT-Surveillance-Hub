#!/usr/bin/python
import sys
import time
import traceback
import common
import subprocess
import re

try:
    while True:

        print "Scanning for nearby bluetooth devices!"
        # Scan for bluetooth devices
        # We need to timeout because lescan will never return
        # CalledProcessError exception is actually means a success because of
        # the timeou interupt
        try:
            output = subprocess.check_output(
                ['timeout', '-s', 'SIGINT', '5s', 'hcitool', 'lescan', '--duplicates'], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            devices = e.output
        except:
            print "Error while scanning for bluetooth devices!"
            raise

        # Parse output and insert into iot-project.db
        try:
            for line in devices.split('\n'):
                if (re.match(r'(\w+:\w+)+', line)):
                    (macaddress, deviceName) = line.split()
                    print "Found Device %s with mac address %s" % (deviceName, macaddress)
                    dbQuery = "INSERT OR REPLACE INTO BluetoothDevices values ('%s','%s',datetime('now'))" % (
                        macaddress, deviceName)
                    common.query(dbQuery)
        except:
            print "Error recording bluetooth devices in DB!"
            raise
        print "Scan complete , sleeping for 60 seconds"
        time.sleep(60)

except:
    print "Error running Bluetooth Scanner!"
    traceback.print_exc()
finally:
    sys.exit()
