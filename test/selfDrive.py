import RPi.GPIO as GPIO
import picamera
import numpy as np
import cv2 as cv
import math
import time
import skimage.io as io
from skimage.util import img_as_float, crop
from skimage.measure import label, regionprops
from skimage.morphology import remove_small_objects

camera = picamera.PiCamera()

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(25, GPIO.OUT)
GPIO.setup(4, GPIO.OUT)

p = GPIO.PWM(25, 50)
p2 = GPIO.PWM(4, 50)

p.start(0)
p2.start(0)

GPIO.output(5, GPIO.LOW)
GPIO.output(6, GPIO.HIGH)

# this class has little parameters for my purposes
# ^ the values right now work just fine ^

class imgProp:
    
    def __init__(self, image):
        
        # opencv 
        self.newImg = cv.imread(image, cv.IMREAD_GRAYSCALE)
        self.newImg = cv.GaussianBlur(self.newImg, (75, 75), 0) 
        notSureWhatThisIsFor, self.bi = cv.threshold(self.newImg, 150, 255, cv.THRESH_BINARY) 
        
        # scikit images
        self.finalImg = img_as_float(self.bi) # transforms opencv image to scikit images
        self.finalImg = label(self.finalImg)
        self.finalImg = remove_small_objects(self.finalImg, 16000, 1) 
        self.finalImg = crop(self.finalImg, ((800, 0), (0, 0)), copy = True) # crops 800 from the height (top, bottom), (left, right)
        
    def error(self):
        
        self.prop = regionprops(self.finalImg)
        # next three lines are only temporary as I check for errors
        self.angleR = 0
        self.angleL = 0
        self.errorLat = 0
        # THIS PORTION IS IF THERE ARE TWO OBJECTS IN THE VIEW
        if len(self.prop) == 2:
            self.boxR = self.prop[0].bbox
            self.boxL = self.prop[1].bbox
            self.boxRBRC = self.boxR[-2:] # BRC is bottom right corner, in (y,x) format
            self.boxLBLC = (400, self.boxL[1]) # BLC is bottom left corner, in (y,x) format
            self.centroidR = self.prop[0].centroid
            self.centroidL = self.prop[1].centroid
            self.angleR = self.prop[0].orientation * (180 / np.pi) + 90
            self.angleL = self.prop[1].orientation * (180 / np.pi) + 90
            self.halfMax = 960 # half of the horizontal resolution of 1920
        
            # Difference between half the resolution and the middle of the bottom of the two objects, positive if car is to the right
            self.errorLat = self.halfMax - ((self.boxLBLC[1] + self.boxRBRC[1]) / 2) 
            #error2 = x1 - x2 # Difference between the middle of the bottom of the two objects and the middle of the top of the two objects, positive if car is turned to the right
            self.error2 = self.errorLat - ((self.centroidR[1] self.centroidL[1]) / 2)
            
            # determine lateral position to gauge where the car should turn
            if self.errorLat > 0: 
                pass # want car to turn left
            else:
                pass # want car to turn right
            
        # THIS PORTION IS IF THERE'S ONLY ONE OBJECT IN THE VIEW AND THAT OBJECT IS SMALL
        # explanation: one object being if the car is off so much it can only see one rope in the cropped view
        # check which line it is sensing by looking at the angle, if angle > 90 then turn left, if angle < 90 then turn right
        elif self.prop[0].orientation > 0: 
            p2.ChangeDutyCycle(2) # turn left
        else:
            p2.ChangeDutyCycle(7.83) # turn right, rough value to turn the same amount as it does turning left since wheels CAN turn more right than left
                
    # if there is one object then that object is large,  it has reached the end of the rope "U" shape       
    def endRun():
        if regionprops(self.finalImg)[0].area >= 75000: # endU.jpg has an area of 1234323
            return True
        return False


    
# --------------------------------------------- #
# main code area
# ----------------------------------------------#

time.sleep(2)

i = 0
# start the car slow so it has enough power to overcome friction 
p.ChangeDutyCycle(40) # not sure what value to use since there's still problems with the motor drive
p2.ChangeDutyCycle(5.8)

while(True):
    
    fstring = f'car{i}.jpg'
    camera.capture(fstring)
    img = imgProp(fstring)
    
    if (img.endRun()):
        p.ChangeDutyCycle = 0
        p2.ChangeDutyCycle = 5.8
        break
    
    else img.error()
    
    del img # deletes object so it can be created again in the next loop + keeps memory usage low?? idk
    i += 1



p.stop()
p2.stop()
GPIO.cleanup()