import RPi.GPIO as GPIO
import time
from gpiozero import Motor

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


GPIO.setup(19, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)

print ("turning motor on")
GPIO.output(19, GPIO.HIGH)
GPIO.output(26, GPIO.LOW)
time.sleep(5)

GPIO.output(19, GPIO.LOW)
GPIO.output(26, GPIO.LOW)
time.sleep(2)

GPIO.output(19, GPIO.LOW)
GPIO.output(26, GPIO.HIGH)
time.sleep(5)


GPIO.output(19, GPIO.LOW)
GPIO.output(26, GPIO.LOW)
time.sleep(2)


GPIO.cleanup()

