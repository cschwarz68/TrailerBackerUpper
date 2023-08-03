from camera import Camera
from state_informer import StateInformer
import cv2
import time
import imutils 
import image_utils as iu
import math
import image_processing as ip
from imutils import contours, perspective
import numpy as np

#distance between objects in an image

if __name__ == "__main__":
    this = StateInformer()
    cam = Camera().start()
    time.sleep(2)
    img = cam.read()
    red = iu.filter_red(img)
    edges = ip.edge_detector(red)
    cntrs = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cntrs = imutils.grab_contours(cntrs)
    (cntrs, _) = contours.sort_contours(cntrs, method = "top_to_bottom")
    red_tape = cntrs[0]
    box = cv2.minAreaRect(red_tape)
    box = cv2.boxPoints(box)
    box = np.array( box, dtype="int")

    box = perspective.order_points(box)
    cX = np.average(box[:,0])
    cY = np.average(box[:,1])

    tl, tr, bl, br = box
    top_mid = iu.midpoint(tl,tr)
    bottom_mid = iu.midpoint(bl,br)

    distance  = math.dist(top_mid, bottom_mid)

    ratio = distance / (7/8) # seven eighths inches lol

    print(ratio)
    print(distance)


  
    cv2.imwrite("contours.png", edges)
    this.stop()
    cam.stop()
