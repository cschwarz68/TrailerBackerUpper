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

p = GPIO.PWM(25, 50) 
p2 = GPIO.PWM(4, 50) #used for turning the front wheels 

p.start(0)
p2.start(0) #Duty cycle starting point 


GPIO.output(5, GPIO.LOW)
GPIO.output(6, GPIO.HIGH)

# Define some colors
darkgrey = (40, 40, 40)
lightgrey = (150, 150, 150)

# Define Forwards Speed, Reverse Speed, and turn angle as neutral positions
sp = -1
rev = -1
dc = 5.8 #used to be 6.1

# This just tests if the program runs on startup

p2.ChangeDutyCycle(10)
time.sleep(1)
p2.ChangeDutyCycle(2)
time.sleep(1)
p2.ChangeDutyCycle(6)
time.sleep(1)

# The program DOES run on startup, the wheels turn right => left => mid 

# This is a simple class that will help us print to the screen
# It has nothing to do with the joysticks, just outputting the
# information.

class TextPrint:
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 20)
 
    def print(self, screen, textString):
        textBitmap = self.font.render(textString, True, lightgrey)
        screen.blit(textBitmap, [self.x, self.y])
        self.y += self.line_height
        
    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15
        
    def indent(self):
        self.x += 10
        
    def unindent(self):
        self.x -= 10
 
# Add selfDrive imgProp Class here 
  
pygame.init()
 
# Set the width and height of the screen [width,height]
size = [500, 980]
screen = pygame.display.set_mode(size)
 
pygame.display.set_caption("Joystick Information")
 
#Loop until the user clicks the close button.
done = False
 
# Used to manage how fast the screen updates
clock = pygame.time.Clock()
 
# Initialize the joysticks
pygame.joystick.init()
    
# Get ready to print
textPrint = TextPrint()
 
# Function to change axis values into Duty Cycle values for Angles
def angle(axis): 
    
    global dc
    dc = axis * 4 + 6
    return dc

# Function to change axis values into Duty Cycle values for Forwards Speed
def forward(axis):
    
    GPIO.output(5, GPIO.LOW)
    GPIO.output(6, GPIO.HIGH)
    
    global sp
    sp = axis * 20 + 80
    return sp

# Function to change axis values into Duty Cycle values for Reverse Speed

def reverse(axis):
    
    GPIO.output(5, GPIO.HIGH)
    GPIO.output(6, GPIO.LOW)
   
    global rev
    rev = axis * 20 + 80
    return rev
 
# -------- Main Program Loop -----------
while done==False:
    
    # EVENT PROCESSING STEP
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            done=True # Flag that we are done so we exit this loop
        
    # Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP
    #JOYHATMOTION
        if event.type == pygame.JOYBUTTONDOWN:
            print("Joystick button pressed.")
        if event.type == pygame.JOYBUTTONUP:
            print("Joystick button released.")
       
    #Get count of joysticks
    joystick_count = pygame.joystick.get_count()
     
    if joystick_count == 0:
        print('No Joystick Detected: Car will automatically begin Driving')
        done = True  
 
    # DRAWING STEP
    # First, clear the screen to white. Don't put other drawing commands
    # above this, or they will be erased with this command.
    screen.fill(darkgrey)
    textPrint.reset()
     
    textPrint.print(screen, "Number of joysticks: {}".format(joystick_count) )
    textPrint.indent()
    
    # For each joystick:
    for i in range(joystick_count):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
    
        textPrint.print(screen, "Joystick {}".format(i) )
        textPrint.indent()
    
        # Get the name from the OS for the controller/joystick
        name = joystick.get_name()
        textPrint.print(screen, "Joystick name: {}".format(name))
        
        # Usually axis run in pairs, up/down for one, and left/right for
        # the other.
        axes = joystick.get_numaxes()
        textPrint.print(screen, "Number of axes: {}".format(axes) )
        textPrint.indent()
    
        for i in range(axes):
           
            axis0 = joystick.get_axis(0) #Left Joystick values were weird one time,
            #so we swapped to right, and now left works just fine after trying again
            axis2 = joystick.get_axis(2)
            axis5 = joystick.get_axis(5)
            axis = joystick.get_axis( i )
            textPrint.print(screen, "Axis {} value: {:>6.0f}".format(i, axis))
            
            if axis0 > 0.1 and axis0 < 0.4:
                p2.ChangeDutyCycle(angle(axis0))
                print('rightLow', axis0, dc)
                
            if axis0 > 0.4 and axis0 < 0.8:
                p2.ChangeDutyCycle(angle(axis0))
                print('rightMid', axis0, dc)
                
            if axis0 > 0.8:
                p2.ChangeDutyCycle(angle(axis0))
                print('rightHigh', axis0, dc)
                
            if axis0 > -0.1 and axis0 < 0.1:
                p2.ChangeDutyCycle(angle(axis0))
                
            if axis0 < -0.1 and axis0 > -0.4:
                p2.ChangeDutyCycle(angle(axis0))
                print('leftLow', axis0, dc)
                
            if axis0 < -0.4 and axis0 > -0.8:
                p2.ChangeDutyCycle(angle(axis0))
                print('leftMid', axis0, dc)
                
            if axis0 < -0.8:
                p2.ChangeDutyCycle(angle(axis0))
                print('leftHigh', axis0, dc)
               
 ############################################################              
               
            if axis5 > 0 and axis5 < 0.4:
                p.ChangeDutyCycle(forward(axis5))
                print('moderate forwards', axis5, sp)
            if axis5 > 0.4 and axis5 < 0.8:
                p.ChangeDutyCycle(forward(axis5))
                print('fast forwards', axis5, sp)
            if axis5 > 0.8:
                p.ChangeDutyCycle(forward(axis5))
                print('very fast forwards', axis5, sp)
                
            if axis5 < -0 and axis5 > -0.4:
                p.ChangeDutyCycle(forward(axis5))
                print('slow forwards', axis5, sp)
            if axis5 < -0.4 and axis5 > -0.75:
                p.ChangeDutyCycle(forward(axis5))
                print('very slow forwards', axis5, sp)
            
            if axis5 < -0.75 and axis5 > -1:
                p.ChangeDutyCycle(0)
                print('stationary', axis5)
                
################################################################

            if axis2 > 0 and axis2 < 0.4:
                p.ChangeDutyCycle(reverse(axis2))
                print('moderate reverse', axis2, rev)
            if axis2 > 0.4 and axis2 < 0.8:
                p.ChangeDutyCycle(reverse(axis2))
                print('fast reverse', axis2, rev)
            if axis2 > 0.8:
                p.ChangeDutyCycle(reverse(axis2))
                print('very fast reverse', axis2, rev)
                
            if axis2 < -0 and axis2 > -0.4:
                p.ChangeDutyCycle(reverse(axis2))
                print('slow reverse', axis2, rev)
            if axis2 < -0.4 and axis2 > -0.75:
                p.ChangeDutyCycle(reverse(axis2))
                print('very slow reverse', axis2, rev)
            
            if axis2 < -0.75 and axis2 > -1:
                p.ChangeDutyCycle(0)
                print('stationary', axis2)
             
                
        textPrint.unindent()
            
        buttons = joystick.get_numbuttons()
        textPrint.print(screen, "Number of buttons: {}".format(buttons) )
        textPrint.indent()
 
        for i in range( buttons ):
            button1 = joystick.get_button(1)
            button = joystick.get_button( i )
            textPrint.print(screen, "Button {} value: {:>6.0f}".format(i,button) )
            
            if button1 == 1:
                print("program ended")
                done = True
                
        textPrint.unindent()
            
        # Hat switch. All or nothing for direction, not like joysticks.
        # Value comes back in an array.
        hats = joystick.get_numhats()
        textPrint.print(screen, "Number of hats: {}".format(hats) )
        textPrint.indent()
 
        for i in range( hats ):
            hat = joystick.get_hat( i )
            textPrint.print(screen, "Hat {} value: {}".format(i, str(hat)) )
        textPrint.print(screen, "")
        
#All of the code is copied except these lines underneath -> just a quick note for our controller
#Thought about doing it in for loops with switch/case statement, but just manually did it
        textPrint.unindent()
        textPrint.unindent()
        textPrint.print(screen, "Key:")
        textPrint.indent()
        textPrint.print(screen, "Axes:")
        textPrint.indent()
        textPrint.print(screen, "Axis 0 = Left Joystick L/R")
        textPrint.print(screen, "Axis 1 = Left Joystick U/D")
        textPrint.print(screen, "Axis 2 = Left Trigger")
        textPrint.print(screen, "Axis 3 = Right Joystick L/R")
        textPrint.print(screen, "Axis 4 = Right Joystick U/D")
        textPrint.print(screen, "Axis 5 = Right Trigger")
        textPrint.unindent()
        textPrint.print(screen, "Buttons:")
        textPrint.indent()
        textPrint.print(screen, "Button 0 = A")
        textPrint.print(screen, "Button 1 = B")
        textPrint.print(screen, "Button 2 = X")
        textPrint.print(screen, "Button 3 = Y")
        textPrint.print(screen, "Button 4 = Left Bumper")
        textPrint.print(screen, "Button 5 = Right Bumper")
        textPrint.print(screen, "Button 6 = Back")
        textPrint.print(screen, "Button 7 = Start")
        textPrint.print(screen, "Button 8 = Logitech")
        textPrint.print(screen, "Button 9 = Left Stick In")
        textPrint.print(screen, "Button 10 = Right Stick In")
        textPrint.unindent()
        textPrint.print(screen, "Hats:")
        textPrint.indent()
        textPrint.print(screen, "Hat 0 = dpad")
        textPrint.indent()
        textPrint.print(screen, "(When the Mode button is pressed, the dpad and left Joystick swap:")
        textPrint.print(screen, "Hat 0 Value becomes the left Joystick")
        textPrint.print(screen, "Axis Values 0-1 become the dpad)")
        textPrint.unindent()
        textPrint.unindent()
        textPrint.unindent()  
        
    # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT
    
    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()
 
    # Limit to 20 frames per second
    clock.tick(20)

pygame.display.quit()
 
# put here selfDrive.py main code area
 
p.stop()
p2.stop()
GPIO.cleanup()