import time
import RPi.GPIO as GPIO
import picamera


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

camera = picamera.PiCamera()

GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(25, GPIO.OUT)
GPIO.setup(4, GPIO.OUT)

p = GPIO.PWM(25, 50) #Frequency of spin/update(refresh) rate of spin
#will make a total # of movements equal to x+1. x = "p = GPIO.PWM(25, x)" 

p2 = GPIO.PWM(4, 50) #Point to which the wheels turn and face (81-2 is about the center)
#Range is approximately 60-150 (farthest right to farthest left)
#This only applies when "p2.start(x)" - x=10. Values are not constant if x is manipulated in any way
#Seems like either PWM value can be changed to accomplish turning to a known set point


p.start(0) #Motor speed. Value of "0" will disable turning
p2.start(0)#Value of "0" will disable turning

camera.start_preview(alpha = 175)

time.sleep(20)

p2.ChangeDutyCycle(5.8)
#Farthest left = 3
#Exact middle = 5.8
#Farthest right = 8.3
time.sleep(0.5)

GPIO.output(5, GPIO.LOW)
GPIO.output(6, GPIO.HIGH)
p.ChangeDutyCycle(75)

time.sleep(3)

'''GPIO.output(5, GPIO.LOW)
GPIO.output(6, GPIO.LOW)

time.sleep(1)

p.start(25)

GPIO.output(5, GPIO.LOW)
GPIO.output(6, GPIO.HIGH)

time.sleep(1)
'''
camera.stop_preview()

'''
p2.ChangeDutyCycle(8)
time.sleep(3)
p2.ChangeDutyCycle(6)
time.sleep(2)
'''

'''
#this isn't exact but it's decently close
#observation: the two wheels aren't parallel with each other
def setAngle(degree): 
    dutyCycle = degree / 18 + 2
    p2.ChangeDutyCycle(dutyCycle)
    time.sleep(2)
    
#setAngle(30)
'''


'''
#testing the different camera opacities
#pivoting the front two wheels
x = 0

for cam in range(15):
    camera.start_preview(alpha = cam * 17) #alpha = value changes the image preview opacity
    #camera.annotate_foreground = picamera.Color('yellow')
    camera.annotate_background = picamera.Color('blue')
    camera.annotate_text = f'This is image preview {cam + 1}'
    
    if x % 2:
        p2.ChangeDutyCycle(5) #left
    else:
        p2.ChangeDutyCycle(7) #right

    x += 1
    
    time.sleep(1)

p2.ChangeDutyCycle(3)
time.sleep(3)
p2.ChangeDutyCycle(6.1)
time.sleep(3)
camera.stop_preview()
'''
'''
#messing around with Camera Zoom, can't find documentation
camera.zoom = (0.05, 0.05, 2, 2)
camera.start_preview(alpha = 175)
camera.annotate_text_size = 75
camera.annotate_text = 'Hey!'
#camera.annotate_foreground = picamera.Color('paleturquoise')
camera.annotate_background = picamera.Color('paleturquoise')
time.sleep(60)
camera.stop_preview()
'''

''
#pivot front wheels left to right, and right to left
#servo moving and camera at the same time
'''
camera.start_preview(alpha = 175)

p2.ChangeDutyCycle(2.5)
time.sleep(3)

for t in range(4, 0, -1):
    for x in range(25,110):
        p2.ChangeDutyCycle(x/10)
        print(x)
        time.sleep(t/150)
    for x in range(110, 25, -1):
        p2.ChangeDutyCycle(x/10)
        print(x)
        time.sleep(t/150)

p2.ChangeDutyCycle(6.1)
time.sleep(3)

camera.stop_preview()
'''
'''
p2.ChangeDutyCycle(2)
time.sleep(15)
p2.ChangeDutyCycle(2.5)
time.sleep(15)
p2.ChangeDutyCycle(5)
time.sleep(15)
p2.ChangeDutyCycle(6)
time.sleep(15)
p2.ChangeDutyCycle(7.5)
time.sleep(15)
p2.ChangeDutyCycle(10)
time.sleep(15)
p2.ChangeDutyCycle(12.5)
time.sleep(15)
'''

p.stop()
p2.stop()
GPIO.cleanup()
    