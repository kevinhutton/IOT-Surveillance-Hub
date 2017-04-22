#!/usr/bin/python
import sys
import RPi.GPIO as GPIO
import time

try:
    loopcount = 0
    # Use broadcom numbering system
    GPIO.setmode(GPIO.BCM)
    # Label GPIO pins used on breadboard.
    # Output pin used to trigger sound wave
    TRIG = 20
    # Input pin used to measure distance
    ECHO = 26

    # Connect the libraries to your GPIO pins
    print("Distance Measurement in Progess")
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)

    # Settle the sensor before beginning
    GPIO.output(TRIG, False)
    time.sleep(2)

    # Send a pulse for 10 microseconds.

    while True:
        # Send 1 signal and then stop
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)

        # Record pulse start time and then wait for echo response
        # The round trip duration will be pulse_start - pulse_end
        pulse_start = time.time()
        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()

        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()
        pulse_duration = pulse_end - pulse_start

        # 34300 cm/s = Distance/Time; 34300 cm/s = Speed of sound;
        # "Time" is there and back; divide by 2 to get time-to-object only.
        # 34300 = Distance/(Time/2) >>> speed of sound = distance/one-way time

        distance = pulse_duration * 17150

        # Round out distance
        distance = round(distance, 2)
        loopcount += 1
        print("Object Detected")
        print("Distance:", distance, "cm")
        time.sleep(1)

except:
    print "Program Interupted!"
finally:
    print "Cleanup GPIO pins"
    GPIO.cleanup()
    sys.exit()
