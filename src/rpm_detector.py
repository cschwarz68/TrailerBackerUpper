import warnings
import math
from time import time_ns, time
from threading import Thread
from camera import Camera
from streaming import FrameSegment
import socket



# Package Imports
import numpy as np
import cv2

#Local Imports
import image_processing as ip

#Horrible terrible spaghetti code module; will make this all not suck before implementing for real


def filter_yellow(img: cv2.Mat) -> cv2.Mat:
    
    # Bitwise complement operator. Flips each bit for each element in the matrix.
    invert = ~img
    hsv = cv2.cvtColor(invert, cv2.COLOR_BGR2HSV)
    lower_cyan = np.array([115, 150, 40])
    upper_cyan = np.array([125, 255, 255])
    # Clamp to certain cyan shades.
    mask = cv2.inRange(hsv, lower_cyan, upper_cyan)
    return mask

def filter_red(img: cv2.Mat) -> cv2.Mat:
    
    # Bitwise complement operator. Flips each bit for each element in the matrix.
    invert = ~img
    hsv = cv2.cvtColor(invert, cv2.COLOR_BGR2HSV)
    lower_cyan = np.array([85, 150, 40])
    upper_cyan = np.array([95, 255, 255])
    # Clamp to certain cyan shades.
    mask = cv2.inRange(hsv, lower_cyan, upper_cyan)
    return mask

def filter_blue(img: cv2.Mat) -> cv2.Mat:
    
    # Bitwise complement operator. Flips each bit for each element in the matrix.
    invert = ~img
    hsv = cv2.cvtColor(invert, cv2.COLOR_BGR2HSV)
    lower_cyan = np.array([20, 220, 225])
    upper_cyan = np.array([30, 230, 230])
    # Clamp to certain cyan shades.
    mask = cv2.inRange(hsv, lower_cyan, upper_cyan)
    return mask


def center_yellow(img: cv2.Mat) -> tuple[float, float]:

    # Contour: structural outlines.
    # Ignoring hierarchy (second return value).
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours)>0:
        big_contour = max(contours, key=cv2.contourArea)
    else:
        return(img.shape[1] / 2, img.shape[0] / 2) #temp fix; bad

    # Moment: imagine the image is a 2D object of varying density. Find the "center of mass" / weighted center of the image.
    moments = cv2.moments(big_contour)
    if (moments["m00"] == 0) or (moments["m00"] == 0):
        return(img.shape[1] / 2, img.shape[0] / 2)
    cx = moments["m10"] / moments["m00"]
    cy = moments["m01"] / moments["m00"]
    return (cx, cy)


    

def update_image(cam):
    start = time_ns()
    image = cam.capture()
    end = time_ns()
    
    filtered = filter_yellow(image)
    return filtered

   
def func(num):
    
    while num>1:
        pass
    
        
def go():
    global cam, avg_color
    #color_wacther = Thread(target = func(avg_color))
    on_screen = False
    off_screen = True
    while True:
        img = update_image(cam)


    
        avg_color_per_row = np.average(img, axis =0)
        avg_color = np.average(avg_color_per_row, axis = 0)
        
        #x,y = center_yellow(img)
        #display_string = '{0:.2f}'.format(x) + ',' + '{0:.2f}'.format(y)
        cv2.putText(img, f"Average Pixel Value: {avg_color}", 
                                (25, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        
        
        start = time_ns()
        
        while avg_color >.5:
            
            img = update_image(cam)
            avg_color_per_row = np.average(img, axis =0)
            avg_color = np.average(avg_color_per_row, axis = 0)
            cv2.putText(img, f"Average Pixel Value: {avg_color}", 
                                (25, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            stream_to_client(img)
        on_time = time_ns()- start
        
        
        start2 = time_ns()
        while avg_color <=.5:
            img = update_image(cam)
            avg_color_per_row = np.average(img, axis =0)
            avg_color = np.average(avg_color_per_row, axis = 0)
            cv2.putText(img, f"Average Pixel Value: {avg_color}", 
                                (25, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            stream_to_client(img)
        off_time = time_ns() - start2

        if off_time < 100000:
            off_time = 0

        if on_time < 100000:
            on_time = 0
        seconds_on = on_time/ 1000000000
        seconds_off = off_time/1000000000
        print(seconds_on, seconds_off, seconds_on +seconds_off) 
        


        
        







def stream_to_client(stream_image: cv2.Mat):
    frame_segment
   
    frame_segment.udp_frame(stream_image)   

if __name__ == "__main__":
    # Streaming
    avg_color = 0
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    port = 25565
    """
    IMPORTANT

    Insert the IP address of the device to stream to.
    """
    addr = "192.168.2.185"
    frame_segment = FrameSegment(server_socket, port, addr)
    cam = Camera()
    interval = 1/15
    go()

   
    

        
        








