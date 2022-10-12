import time
import RPi.GPIO as GPIO
import picamera

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(4, GPIO.OUT)

#Led for testing:
#GPIO.setup(21,GPIO.OUT)

p2 = GPIO.PWM(4, 50)
p2.start(0)

p2.ChangeDutyCycle(2)
#GPIO.output(21,GPIO.LOW)
time.sleep(0.4)
#GPIO.output(21,GPIO.HIGH)
p2.ChangeDutyCycle(8)
time.sleep(0.4)
#GPIO.output(21,GPIO.LOW)
p2.ChangeDutyCycle(6)
time.sleep(0.5)

p2.stop()

GPIO.cleanup()