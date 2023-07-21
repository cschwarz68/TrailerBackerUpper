import warnings
import math
from time import time_ns, time, sleep
from threading import Thread
from threaded_camera import Camera
from streaming import FrameSegment
import socket




# Package Imports
import numpy as np
import cv2

#Local Imports
import image_processing as ip

# Horrible terrible spaghetti code module; will make this all not suck before implementing for real.
# My plan is to implement the functionality of this module main or maybe image processing and then delete this file


def filter_yellow(img: cv2.Mat) -> cv2.Mat:
    
    # Bitwise complement operator. Flips each bit for each element in the matrix.
    invert = ~img
    hsv = cv2.cvtColor(invert, cv2.COLOR_RGB2HSV)
    lower_cyan = np.array([115, 150, 40])
    upper_cyan = np.array([125, 255, 255])
    # Clamp to certain cyan shades.
    mask = cv2.inRange(hsv, lower_cyan, upper_cyan)
    return mask






    

def update_image(cam: Camera):
    
    image = cam.read()
    
    
    filtered = filter_yellow(image)
    return filtered

   
def go():
    while True:
        image = cam.read()
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        yellow = filter_yellow(image)
        red = ip.filter_red(image)
        red_x, red_y = ip.weighted_center(red)
        yellow_x, yellow_y = ip.weighted_center(yellow)
        combined = ip.combine_images([(yellow,1),(red, 1)])
        ip.put_text(combined, f"{yellow_x} {yellow_y}")
        if int(yellow_y) in range(int(red_y)-10, int(red_y)+10):
            
            ip.put_text(combined, "passing", (50,50))

        #print(red_y, yellow_y)
        
        stream_to_client(combined)
    
        



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
    cam = Camera().start()
    
    sleep(2)
    interval = 1/15
    if 6 in range(int(2)-5, int(2)+5):
        print('duh')
    #exit(0)
    go()

   
