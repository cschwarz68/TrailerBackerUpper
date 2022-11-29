import pygame
import RPi.GPIO as GPIO
import time
# add selfDrive imports
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(25,GPIO.OUT)
GPIO.setup(4, GPIO.OUT) #used to be 13

#Initializing
#Get count of joysticks
joystick_count = pygame.joystick.get_count()
#Get number of axes
axes = joystick.get_numaxes()
textPrint.print(screen, "Number of axes: {}".format(axes) )
textPrint.indent()
#controller loop
def controller_main():
    pass
if __name__=="__main__":
    controller_main