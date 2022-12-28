#imports
import cv2
import numpy as np
import os
from os import listdir
from matplotlib import pyplot as plt
import matplotlib.image as mpimg
import skimage
from skimage.util import img_as_float
from skimage.measure import regionprops, label
from skimage.morphology import remove_small_objects
from PIL import Image
#initialize folder
folder_dir = "/Users/adimukundan/Documents/GitHub/TrailerBackerUpper/test/assets"
#initialize image name array
names = []
for image in os.listdir(folder_dir):
    names.append(image)
#initialize image files array
files = []
for name in names:
    image = mpimg.imread("/Users/adimukundan/Documents/GitHub/TrailerBackerUpper/test/assets/"+name)
    files.append(image)
#initialize plot
fig = plt.figure(figsize=(10, 7))
rows = 3
columns = 4
#display initial images
for i in range(len(names)):
    fig.add_subplot(rows, columns, i+1)
    plt.imshow(files[i])
    plt.axis('off')
    plt.title(i)
plt.show()
'''
gray = cv2.cvtColor(files[0], cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (45, 45), 0)
ret, binary = cv2.threshold(blur, 150, 255, cv2.THRESH_BINARY)
#remove small objects
float = img_as_float(binary)
label_float = label(float)
filtered = remove_small_objects(label_float, 16000, 1)
#show image
imgPlot = plt.imshow(filtered)
plt.show()
#cv2.imshow("unblur", files[0])
#cv2.imshow("filtered", filteredImage)
#cv2.waitKey(0)
#cv2.destroyAllWindows()
#initialize image
#image = cv2.imread("/Users/adimukundan/Documents/GitHub/TrailerBackerUpper/src/testimage.jpeg", cv2.IMREAD_GRAYSCALE)
'''
#function to modify image
def imageChanger(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (45, 45), 0)
    ret, binary = cv2.threshold(blur, 150, 255, cv2.THRESH_BINARY)
    float = img_as_float(binary)
    labelFloat = label(float)
    filtered = remove_small_objects(labelFloat, 16000, 1)
    return filtered
def measureAngles(img):
    prop = regionprops(img)
    if (len(prop) >= 2):
        boxR = prop[0].bbox
        boxL = prop[1].bbox
        boxRBRC = boxR[-2:]
        boxLBLC = (400, boxL[1])
        centroidR = prop[0].centroid
        centroidL = prop[1].centroid
        angleR = prop[0].orientation * (180 / np.pi) + 90
        angleL = prop[1].orientation * (180 / np.pi) + 90
        halfMax = 960
        errorLat = halfMax - ((boxLBLC[1] + boxRBRC[1]) / 2)
        print(angleR, angleL)

finalFig = plt.figure(figsize=(10, 7))
finalArray = []
for name in names:
    image = mpimg.imread("/Users/adimukundan/Documents/GitHub/TrailerBackerUpper/test/assets/"+name)
    finalArray.append(imageChanger(image))
    measureAngles(imageChanger(image))
for i in range(len(finalArray)):
    finalFig.add_subplot(rows, columns, i+1)
    plt.imshow(finalArray[i])
    plt.axis('off')
    plt.title(i)
plt.show()
def processing_test():
    blur = cv2.GaussianBlur(image, (5, 5), 0)
    ret, thresh_binary = cv2.threshold(blur,127,255,cv2.THRESH_BINARY)
    ret, thresh_binary_2 = cv2.threshold(blur,150, 255,cv2.THRESH_BINARY)
    ret, otsu = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    '''
    edges = cv2.Canny(blur, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=50, maxLineGap=10)
    line1 = lines[0]
    line2 = lines[1]
    points1 = np.array([[line1[0][0], line1[0][1]], [line1[0][2], line1[0][3]]])
    points2 = np.array([[line2[0][0], line2[0][1]], [line2[0][2], line2[0][3]]])
    [vx1, vy1, x1, y1] = cv2.fitLine(points1, cv2.DIST_L2, 0, 0.01, 0.01)
    [vx2, vy2, x2, y2] = cv2.fitLine(points2, cv2.DIST_L2, 0, 0.01, 0.01)
    angle = np.arctan2(vy1, vx1) - np.arctan2(vy2, vx2)
    angle = np.rad2deg(angle)
    print('Angle between lines:', angle)
    for line in lines:
        x1, y1, x2, y2 = line[0]
        cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    '''
    cv2.imshow('thresh', thresh_binary)
    cv2.imshow('thresh2', thresh_binary_2)
    cv2.imshow("otsu", otsu)
    cv2.imshow("original", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
if __name__=="__main__":
    
    #processing_test()
    pass