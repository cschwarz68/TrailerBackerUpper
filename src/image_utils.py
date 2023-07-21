import cv2
import numpy as np

class RGBColor:
    def __init__(self, R: int, G: int, B: int):
        self.R = R
        self.G = G
        self.B = B

    def toHSV(self):

        # I didn't want to type `self.` a million times
        R = self.R 
        G = self.G 
        B = self.B 
        maximum = max((R, G, B))
        minimum = min((R, G, B))

        math_that_i_use_twice = np.arccos((R - G/2 - B/2) / np.sqrt(R**2 + G**2 + B ** 2 - R*G - R*B - G*B)) * 180/np.pi

        H =  math_that_i_use_twice/2 if G >= B else (360 - math_that_i_use_twice)/2 # divide by 2 because opencv HSV range is [0,180]
        S = (1 - minimum/maximum) * 255 if maximum > 0 else 0
        V = maximum

        # Source: https://www.had2know.org/technology/hsv-rgb-conversion-formula-calculator.html

        return HSVColor(int(H), int(S), int(V))
    
    def get_tuple(self):
        return (self.R, self.G, self.B)
    
class HSVColor:
    def __init__(self, H: int, S: int, V: int):
        self.H = H
        self.S = S 
        self.V = V
    
    def get_tuple(self):
        return self.H, self.S, self.V
    
    def toRGB(self):
       H = self.H 
       S = self.S
       V = self.V
       maximum = 255*self 
    
    def invert(self):
        pass




    
 
        


# Filters image for red by inverting image so red --> cyan. 
# Uses HSV format to be able to only include certain saturation and brightness of cyan.
def filter_red(img: cv2.Mat) -> cv2.Mat:
    
    
    # Bitwise complement operator. Flips each bit for each element in the matrix.
    invert = ~img
    hsv = cv2.cvtColor(invert, cv2.COLOR_BGR2HSV)
    lower_cyan = np.array([85, 100, 40]) # Lower bound of HSV values to include in mask
    upper_cyan = np.array([95, 255, 255]) # Upper bound of HSV values to include in mask
    # Clamp to certain cyan shades.
    mask = cv2.inRange(hsv, lower_cyan, upper_cyan)
    return mask

def filter_for_color(img : cv2.Mat, lower_color: HSVColor, upper_color: HSVColor):
    # Filters an image for a specified color. `ranges`

    # Get inverse of color and convert to HSV since we look at the inverted image below
    def get_HSV_of_inverse(color: Color):
        R, G, B = color.get_RGB_tuple()
        inverse_color = (~R, ~G, ~B)
        H,S,V = Color(*inverse_color).get_HSV_tuple()
        return H,S,V
    
    lower_H, lower_S, lower_V = get_HSV_of_inverse(lower_color)
    upper_H, upper_S, upper_V = get_HSV_of_inverse(upper_color)
    
    


    # Bitwise complement operator. Flips each bit for each element in the matrix.
    invert = ~img
    hsv = cv2.cvtColor(invert, cv2.COLOR_BGR2HSV)
    lower_bound = np.array([lower_H, lower_S, lower_V]) # Lower bound of HSV values to include in mask
    upper_bound = np.array([upper_H, upper_S, upper_V]) # Upper bound of HSV values to include in mask
    # Clamp to colors in between bounds
    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    return mask




# Finds the weighted center of the image. Images filtered for certain colors should be passed here to find the coordinates of colored markers.
def weighted_center(img: cv2.Mat) -> tuple[float, float]:

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