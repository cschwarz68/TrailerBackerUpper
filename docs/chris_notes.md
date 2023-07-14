Disclaimer: This is going to be way worse than Alex's far superior note file.

ISSUE: Controller disconnects when camera is also active.
    PROBABLE CAUSE: 
        We thought this was due to voltage drop. I now think this is not the case.
        Firstly, upon instantiation of a Camera object, the camera is being powered whether it is capturing or not.
        Secondly, and more convincingly, I have been working on a system to detect vehicle speed by looking at the wheels of the trailer.
        To test it, I disabled the camera functionality in main, ran main to control the vehicle manually, then ran my RPM detector code from a separate module.
        I saw no performance drop in control inputs in main, and the camera was not only on, but the images were being actively processed by some opencv functions, as well as streamed over UDP.
        Recall that "CONTROLLER DISCONNECTED" is printed when update_input() throws an exception, not necessarily when the USB is pulled out (a voltage drop would be equivalent to pulling the USB out).
        It is possible the exception is actually caused by something other than a controller disconnect, and we never bothered to check.

        UPDATE: The exception was due to a key error for an event code SYN_DROPPED which I did not include in my keymap in gamepad.py.
        This code is "Used to indicate buffer overrun in the evdev client’s event queue.
        Client should ignore all events up to and including next SYN_REPORT event and query the device (using EVIOCG* ioctls) to obtain its current state."

        I now think this might be the issue: The loop in which a camera.capture() request is made attempts to take a caputre much faster than the framerate of the camera.
        the VideoCapture class of opencv seems to handle this by returning a `ret` flag to indicate if a new frame has been returned, and returning a frame with value None if 
        a video source has not returned a new capture. Picamera2 does not seem to have this functionality. I think it may just hang until a frame is returned, and supplied inputs fill
        the buffer mentioned above.

        UPDATE 2: Pretty much confirmed what is written in the above paragraph. Attempted to pass button inputs while capturing, and there was no noticable problem.
        Sticks provide thousands of inputs per second, so at a frame rate of 15 FPS, the input buffer can easily fill in one fifteenth of a second, causing SYN_DROPPED.

    POTENTIAL SOLUTION(S): 
       In manual mode, handle camera capture in a separate thread.

    CURRENT STATUS:
        Fixed


I started writing thinking I would not actually succeed in discovering the problem but now I'm pretty sure this is right so I guess I'll maybe implement this fix later.
I think I will leave the note file here because otherwise I would be deleting it literally as soona as I finished writing and that just feels like a huge waste of time.

PS look at me actually documenting a problem and the steps to its solution instead of just internally whining until I solve it.



IDEA: Handle all image processing in separate thread
Image processing  (more generally, I/O) is the slowest part of this operation. Taking the load of image processing off of the main thread could considerable improve performance.
(I do notice some latency in lane detection at times and with my plans to add speed detection, the image processing load will only get heavier.)

We have 4 cores so why not use them? ie, should I use the multiprocessing module instead of threading module? Tasks are IO bound so threading is fine I think??? 



PROBLEM: RPM detection is sort of terribke

    Wasn't even sure if it was possible with our setup so I initially had an extremely naive solution: Put a colored paper over some of the wheel. Measure the time the colored paper is visble, and the time the colored paper is not visible, add the two together for a rotation. Implemented it horribly with loops that would halt anything else from happening but it sort of maybe detected the speed.

    Ideally, I would check when the coordinates of the yellow pass a fixed point. Each pass would correspond to one rotation, and the time between passes would be the duration of a wheel rotation.

    Epic realization that took me way too long to notice: The wheel operates relative to the trailer, and we already have a marker which is fixed to the trailer: the red tape. By using the relative position of the yellow wheel marker to the red trailer marker, I can implement the system where I make note of passes of the yellow past a fixed point.

    Note: The way we are detecting coordinates of colored markers is by filtering the image for only that color, and finding the centroid of the image. When the yellow is not visible,
    the center will just be the middle of the frame. I plan on handling this by checking the level of blackness/whiteness (average pixel value of the image) in the image, and only considering the center when the whiteness is higher than a certain thresold.