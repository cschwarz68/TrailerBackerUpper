import time
import RPi.GPIO as GPIO
import picamera
import pygame
import sys

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

'''
pygame.joystick.init()
print (bool(pygame.joystick.get_init))
print (pygame.joystick.get_count())

joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
print (joysticks)

joystick1 = pygame.joystick.Joystick(0)
joystick1.init()

joystick2 = pygame.joystick.Joystick(0)
joystick2.init()

print (joystick1.get_init())
print (joystick1.get_id())
print (joystick1.get_axis(1))
print (joystick1.get_name())
print (joystick1.get_numaxes())
print (joystick1.get_numballs())
print (joystick1.get_numbuttons())
print (joystick1.get_numhats())
#pygame.event.pump()
print (joystick1.get_axis(0))
'''


#camera = picamera.PiCamera()
#camera.rotation = 180
GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(25, GPIO.OUT)
GPIO.setup(4, GPIO.OUT)#used to be 13

p = GPIO.PWM(25, 50)  #movement motor speed
p2 = GPIO.PWM(4, 50) #turning

p.start(100)
p2.start(100)


GPIO.output(5, GPIO.LOW)
GPIO.output(6, GPIO.LOW)
p.ChangeDutyCycle(100)
p2.ChangeDutyCycle(4.2)

#camera.start_preview()
p.ChangeDutyCycle(30)
GPIO.output(5, GPIO.HIGH)
GPIO.output(6, GPIO.LOW)
#p.ChangeDutyCycle(30)
p2.ChangeDutyCycle(8)

#if <6.1%, turns left
#if ~6.1, neutral
#if >6.1%, turns right

time.sleep(2)
#camera.stop_preview()
GPIO.output(5, GPIO.LOW)
GPIO.output(6, GPIO.LOW)
p2.ChangeDutyCycle(5.6)

time.sleep(0.5)

p.stop()
p2.stop()
GPIO.cleanup()