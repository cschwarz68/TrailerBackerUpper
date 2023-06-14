import numpy as np
import cv2 as cv
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import skimage.io as io
import math
from skimage.util import img_as_ubyte, img_as_float, crop
from skimage.measure import label, regionprops, regionprops_table
from skimage.morphology import remove_small_objects
from skimage.color import label2rgb
from IPython.display import display


# Resizes the image, not sure if it changes the resolution or not
def scaler(image, scale): 
    width = int(image.shape[1] * scale / 100)
    height = int(image.shape[0] * scale / 100)
    dimentions = (width, height)
    scaled_image = cv.resize(image, dimentions, interpolation = cv.INTER_NEAREST)
    return scaled_image
   
def blurrer(image, blur):
    blurred_image = cv.GaussianBlur(image, (blur, blur), 0)
    return blurred_image
   
def edges(image, threshold1, threshold2):
    edges_image = cv.Canny(image, threshold1, threshold2)
    return edges_image

def grayBin(image, blur, threshold1, threshold2): 
    gray_image = cv.imread(image, cv.IMREAD_GRAYSCALE)
    blur_image = cv.GaussianBlur(gray_image, (blur, blur), 0)
    notSureWhatThisIsFor, binary_image = cv.threshold(blur_image, threshold1, threshold2, cv.THRESH_BINARY)
    return binary_image

# Changes OpenCV image to Scikit image
def toScikit(image):
    imageScikit = img_as_float(image)
    return imageScikit

# Changes Scikit image to OpenCV image
def toOpenCV(image):
    imageOpenCV = img_as_ubyte(image)
    return imageOpenCV

def removeSmall(image, size, connecting):
    small = remove_small_objects(image, size, connecting)
    return small

def cropSize(image, top, bottom, left, right, cop):
    cropped = crop(image, ((top, bottom), (left, right)), copy = cop)


# ---------------------------------------------------------------------
# more significant here

# THIS CLASS HAS NO PARAMETERS FOR MY PURPOSES
# IF YOU WOULD LIKE TO VARY THE BLUR, CROP, OR THRESHOLDS, ADD PARAMETERS FOR DIFFERENT imgProp OBJECTS, ADD PARAMETERS
class imgProp:
    
    def __init__(self, image):
        self.newImg = image
    
    
    
    def imgChange(self):
        
        self.newImg = cv.imread(self.newImg, cv.IMREAD_GRAYSCALE)
        self.newImg = cv.GaussianBlur(self.newImg, (75, 75), 0)
        notSureWhatThisIsFor, self.bi = cv.threshold(self.newImg, 150, 255, cv.THRESH_BINARY)
        
        self.finalImg = img_as_float(self.bi)
        self.finalImg = label(self.finalImg)
        self.finalImg = remove_small_objects(self.finalImg, 16000, 1)
        self.finalImg = crop(self.finalImg, ((800, 0), (0, 0)), copy = True)
        
        return self.finalImg
        
    def error(self):
        
        self.prop = regionprops(self.finalImg)
        # next three lines are only temp as I check for errors
        self.angleR = 0
        self.angleL = 0
        self.errorLat = 0
        # THIS PORTION IS IF THERE ARE TWO OBJECTS IN THE VIEW
        if len(self.prop) == 2:
            self.prop = regionprops(self.finalImg)
            self.boxR = self.prop[0].bbox
            self.boxL = self.prop[1].bbox
            self.boxRBRC = self.boxR[-2:] # BRC is bottom right corner, in (y,x) format
            self.boxLBLC = (400, self.boxL[1]) # BLC is bottom left corner, in (y,x) format
            self.centroidR = self.prop[0].centroid
            self.centroidL = self.prop[1].centroid
            self.angleR = self.prop[0].orientation * (180 / np.pi) + 90
            self.angleL = self.prop[1].orientation * (180 / np.pi) + 90
            self.halfMax = 960
        
            # Difference between half the resolution and the middle of the bottom of the two objects, positive if car is to the right
            self.errorLat = self.halfMax - ((self.boxLBLC[1] + self.boxRBRC[1]) / 2) 
            
     
        #error2 = x1 - x2 # Difference between the middle of the bottom of the two objects and the middle of the top of the two objects, positive if car is to the right
        
        # THIS PORTION IS IF THERE'S ONLY ONE OBJECT IN THE VIEW AND THAT OBJECT IS SMALL
        # explanation: one object being if the car is off so much it can only see one rope in the cropped view
        # if there is one object and that object is large, then it has reached the end of the rope "U" shape because it will consider that entire thing just one object
        
        elif len(self.prop) == 1 and regionprops(self.finalImg)[0].area >= 90000: # endU.jpg has an area of 1234323
            pass
        else:
            pass # stop the car since the end of the track has been reached
   

img = cv.imread('ropes.jpg', cv.IMREAD_GRAYSCALE)
imgSlant = cv.imread('e2left.jpg', cv.IMREAD_GRAYSCALE)

#scaled = scaler(img, 25) #see if the resolution is differnet than original full size image

# Blurred image
blur = blurrer(img, 75) # cv.GaussianBlur(img,(75,75),0) <- the original command, however I turned it into a funtion
slantBlur = blurrer(imgSlant, 75)

ret4,th4 = cv.threshold(blur, 150, 255, cv.THRESH_BINARY)
ret5,th5 = cv.threshold(slantBlur, 150, 255, cv.THRESH_BINARY)
th6 = grayBin('straight14.jpg', 75, 150, 255)
th7 = grayBin('e2right.jpg', 75, 150, 255)


#edges4 = edges(th4, 50, 255) # cv.Canny(th4, 100, 200) <- the original command, however I turned it into a funtion 


# Labeled Regions
th4Scikit = toScikit(th4)
th5Scikit = toScikit(th5)
th6Scikit = toScikit(th6)
th7Scikit = toScikit(th7)

label_image = label(th4Scikit)
label_slant = label(th5Scikit)
label_6 = label(th6Scikit)
label_7 = label(th7Scikit)

# Remove the smaller irrelevant blobs
label_imageLarge = remove_small_objects(label_image,  16000, 1)
label_slantLarge = removeSmall(label_slant, 20000, 1)
label_6Large = removeSmall(label_6, 16000, 1)
label_7Large = removeSmall(label_7, 16000, 1)


# Crops the image
# Don't think we need to use this if we remove the small blobs
# HOWEVER this can be used so we detect the end of the rope "U" shape later
label_imageCrop = crop(th4Scikit, ((300, 0), (0, 0)), copy = True) #first tuple crops (top, bottom), second tuple crops (left, right)
label_6LargeCrop = crop(label_6Large, ((800, 0), (0, 0)), copy = True)
label_7LargeCrop = crop(label_7Large, ((800, 0), (0, 0)), copy = True)

#image_label_overlay = label2rgb(label_image,  bg_label = 0) # this changes the color, not entirely sure how it works, but it does
endU = imgProp('endU.jpg')
endU.imgChange()
testClass = imgProp('straight14.jpg')
testClass.imgChange()
e1lefte2right = imgProp('e1lefte2right.jpg')
e1lefte2right.imgChange()
e2right = imgProp('e2right.jpg')
e2right.imgChange()
e1righte2left = imgProp('e1righte2left.jpg')
e1righte2left.imgChange()
e1lefte2left = imgProp('e1lefte2left.jpg')
e1lefte2left.imgChange()
e1righte2right = imgProp('e1righte2right.jpg')
e1righte2right.imgChange()
e1right = imgProp('e1right.jpg')
e1right.imgChange()
e1left = imgProp('e1left.jpg')
e1left.imgChange()
e2left = imgProp('e2left.jpg')
e2left.imgChange()


fig, (ax1, ax2, ax3, ax4) = plt.subplots(ncols = 4, figsize=(15, 9), sharex = True, sharey = True)
ax1.imshow(label_6Large)
ax2.imshow(label_7Large)
ax3.imshow(label_6LargeCrop)
ax4.imshow(label_7LargeCrop)
ax1.set_title('Straight')
ax2.set_title('e2right')
ax3.set_title('Straight cropped')
ax4.set_title('e2right cropped')


for region in regionprops(label_6Large):
    
   
        minr, minc, maxr, maxc = region.bbox
        rect = mpatches.Rectangle((minc, minr), maxc - minc, maxr - minr, fill=False, edgecolor='red', linewidth=2)
        ax1.add_patch(rect)
        
        y0, x0 = region.centroid
        orientation = region.orientation
        x1 = x0 + math.cos(orientation) * 0.5 * region.axis_minor_length
        y1 = y0 - math.sin(orientation) * 0.5 * region.axis_minor_length
        x2 = x0 - math.sin(orientation) * 0.5 * region.axis_major_length
        y2 = y0 - math.cos(orientation) * 0.5 * region.axis_major_length

        ax1.plot((x0, x1), (y0, y1), '-r', linewidth = 2)
        ax1.plot((x0, x2), (y0, y2), '-r', linewidth = 2)
        ax1.plot(x0, y0, '.g', markersize = 5)

        bx = (minc, maxc, maxc, minc, minc)
        by = (minr, minr, maxr, maxr, minr)
        ax1.plot(bx, by, '-b', linewidth = 2)
        
        majorAxisDegree = orientation * (180 / np.pi) + 90
        print('Angle = ', majorAxisDegree)

for region in regionprops(label_7Large):
    
    
        minr, minc, maxr, maxc = region.bbox
        rect = mpatches.Rectangle((minc, minr), maxc - minc, maxr - minr, fill=False, edgecolor='red', linewidth=2)
        ax2.add_patch(rect)
        
        y0, x0 = region.centroid
        orientation = region.orientation
        x1 = x0 + math.cos(orientation) * 0.5 * region.axis_minor_length
        y1 = y0 - math.sin(orientation) * 0.5 * region.axis_minor_length
        x2 = x0 - math.sin(orientation) * 0.5 * region.axis_major_length
        y2 = y0 - math.cos(orientation) * 0.5 * region.axis_major_length

        ax2.plot((x0, x1), (y0, y1), '-r', linewidth = 2)
        ax2.plot((x0, x2), (y0, y2), '-r', linewidth = 2)
        ax2.plot(x0, y0, '.g', markersize = 5)

        bx = (minc, maxc, maxc, minc, minc)
        by = (minr, minr, maxr, maxr, minr)
        ax2.plot(bx, by, '-b', linewidth = 2)
        
        majorAxisDegree = orientation * (180 / np.pi) + 90
        print('Angle = ', majorAxisDegree)

for region in regionprops(label_6LargeCrop):
    
    
        minr, minc, maxr, maxc = region.bbox
        rect = mpatches.Rectangle((minc, minr), maxc - minc, maxr - minr, fill=False, edgecolor='red', linewidth=2)
        ax3.add_patch(rect)
        
        y0, x0 = region.centroid
        orientation = region.orientation
        x1 = x0 + math.cos(orientation) * 0.5 * region.axis_minor_length
        y1 = y0 - math.sin(orientation) * 0.5 * region.axis_minor_length
        x2 = x0 - math.sin(orientation) * 0.5 * region.axis_major_length
        y2 = y0 - math.cos(orientation) * 0.5 * region.axis_major_length

        ax3.plot((x0, x1), (y0, y1), '-r', linewidth = 2)
        ax3.plot((x0, x2), (y0, y2), '-r', linewidth = 2)
        ax3.plot(x0, y0, '.g', markersize = 5)

        bx = (minc, maxc, maxc, minc, minc)
        by = (minr, minr, maxr, maxr, minr)
        ax3.plot(bx, by, '-b', linewidth = 2)
        
        majorAxisDegree = orientation * (180 / np.pi) + 90
        print('Angle = ', majorAxisDegree)
        
for region in regionprops(label_7LargeCrop):
    
    
        minr, minc, maxr, maxc = region.bbox
        rect = mpatches.Rectangle((minc, minr), maxc - minc, maxr - minr, fill=False, edgecolor='red', linewidth=2)
        ax4.add_patch(rect)
        
        y0, x0 = region.centroid
        orientation = region.orientation
        x1 = x0 + math.cos(orientation) * 0.5 * region.axis_minor_length
        y1 = y0 - math.sin(orientation) * 0.5 * region.axis_minor_length
        x2 = x0 - math.sin(orientation) * 0.5 * region.axis_major_length
        y2 = y0 - math.cos(orientation) * 0.5 * region.axis_major_length

        ax4.plot((x0, x1), (y0, y1), '-r', linewidth = 2)
        ax4.plot((x0, x2), (y0, y2), '-r', linewidth = 2)
        ax4.plot(x0, y0, '.g', markersize = 5)

        bx = (minc, maxc, maxc, minc, minc)
        by = (minr, minr, maxr, maxr, minr)
        ax4.plot(bx, by, '-b', linewidth = 2)
        
        majorAxisDegree = orientation * (180 / np.pi) + 90
        print('Angle = ', majorAxisDegree)



prop1 = regionprops_table(label_6Large, properties=('centroid', 'orientation', 'axis_major_length', 'axis_minor_length'))
df1 = pd.DataFrame(prop1)
display(df1)


prop2 = regionprops_table(label_7Large, properties=('centroid', 'orientation', 'axis_major_length', 'axis_minor_length'))
df2 = pd.DataFrame(prop2)
display(df2)

prop3 = regionprops_table(label_6LargeCrop, properties=('centroid', 'orientation', 'axis_major_length', 'axis_minor_length'))
df3 = pd.DataFrame(prop3)
display(df3)

prop4 = regionprops_table(label_7LargeCrop, properties=('centroid', 'orientation', 'axis_major_length', 'axis_minor_length'))
df4 = pd.DataFrame(prop4)
display(df4)



testClass.error()
print(testClass.errorLat)
print(testClass.angleR)
print(testClass.angleL)
print(testClass.prop[0].orientation)
print(testClass.prop[1].orientation)
e1lefte2right.error()
print(e1lefte2right.errorLat)
print(e1lefte2right.angleR)
print(e1lefte2right.angleL)
print(e1lefte2right.prop[0].orientation)
print(e1lefte2right.prop[1].orientation)
e2right.error()
print(e2right.errorLat)
print(e2right.angleR)
print(e2right.angleL)
print(e2right.prop[0].orientation)
print(e2right.prop[1].orientation)
e1righte2left.error()
print(e1righte2left.errorLat)
print(e1righte2left.angleR)
print(e1righte2left.angleL)
print(e1righte2left.prop[0].orientation)
print(e1righte2left.prop[1].orientation)
e1lefte2left.error()
print(e1lefte2left.errorLat)
print(e1lefte2left.angleR)
print(e1lefte2left.angleL)
print(e1lefte2left.prop[0].orientation)
print(e1lefte2left.prop[1].orientation)
e1righte2right.error()
print(e1righte2right.errorLat)
print(e1righte2right.angleR)
print(e1righte2right.angleL)
e1right.error()
print(e1right.errorLat)
print(e1right.angleR)
print(e1right.angleL)
print(e1right.prop[0].orientation)
print(e1right.prop[1].orientation)
e1left.error()
print(e1left.errorLat)
print(e1left.angleR)
print(e1left.angleL)
print(e1left.prop[0].orientation)
print(e1left.prop[1].orientation)
e2left.error()
print(e2left.errorLat)
print(e2left.angleR)
print(e2left.angleL)
print(e2left.prop[0].orientation)
print(e2left.prop[1].orientation)
print(regionprops(endU.finalImg)[0].area)
print(regionprops(e2right.finalImg)[0].area)
# Idea: use the orientation of the regions to determine when the path is turning or is slanted
# Next step is to create a method that finds the orientation (in degrees) of the ropes
# Then find a threshold angle which would change the wheel's direction when going over/under
# While Loop
'''
while (#end of rope "U" shape isn't visible):
    
    # Create Threshold Value
    # Take picture
    # Find orientation in angle
    if (angle is greater/lower than Threshold value):
        # Change Duty Cycle of the wheels so that it stays within the lines



'''

'''
ax1.set_axis_off()
ax2.set_axis_off()
ax3.set_axis_off()
ax4.set_axis_off()
'''


plt.tight_layout()
plt.show()

'''
# Show the Images
cv.imshow('image', scaler(img, 25))
cv.imshow('blurred image', scaler(blur, 25))
cv.imshow('blurred binary th4', scaler(th4, 25))
cv.imshow('slant', scaler(imgSlant, 25))
cv.imshow('blurred slant', scaler(slantBlur, 25))
cv.imshow('blurred binary slant', scaler(th5, 25))
#cv.imshow('boxed', scaler(th4backToOpenCV, 25))
'''






cv.waitKey(0)
cv.destroyAllWindows()




