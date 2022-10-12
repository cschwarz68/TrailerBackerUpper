import time
import RPi.GPIO as GPIO
from gpiozero import Motor


'''
motor = Motor(17, 18)

motor.forward()
#time.sleep(3)
'''

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(25, GPIO.OUT)

p = GPIO.PWM(25, 50)
p.start(0)

GPIO.output(5, GPIO.LOW)
GPIO.output(6, GPIO.LOW)
p.ChangeDutyCycle(30)
time.sleep(2)

print ("turning motor on")

GPIO.output(5, GPIO.HIGH)
GPIO.output(6, GPIO.LOW)
time.sleep(2)

GPIO.output(5, GPIO.LOW)
GPIO.output(6, GPIO.LOW)
time.sleep(2)


GPIO.cleanup()
