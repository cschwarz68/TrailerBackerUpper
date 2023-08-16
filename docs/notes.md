# These are some notes about the repository.
> Will turn into proper documentation.

## IMPORTS

Module: time  
	This module provides various time-related functions.

Module: ~~logging~~ ( unused)  
	This module defines functions and classes which implement a flexible event logging system for applications and libraries.

Library: [`inputs`](https://pypi.org/project/inputs/)  
	Inputs aims to provide cross-platform Python support for keyboards, mice and gamepads.

Library: [`cv2`](https://opencv.org/)\
	OpenCV is a library of programming functions mainly for real-time computer vision.

Library: [`numpy`](https://numpy.org)\
	The fundamental package for scientific computing with Python.

Library: ~~matplotlib~~ (unused)  
	Matplotlib is a comprehensive library for creating static, animated, and interactive visualizations in Python. Matplotlib makes easy things easy and hard things possible.

Library: ~~RPi.GPIO~~ [`pigpio`](http://abyz.me.uk/rpi/pigpio/)\
	This package provides a Python module to control the GPIO on a Raspberry Pi.

Module: ~~drive_module~~ --> [`truck`](../src/truck.py)\
	Controls drivetrain with PWM.
	The functionality of this module has been deprecated by car.py.

Module: ~~steer_module~~ --> [`truck`](../src/truck.py)\
	Controls steering with servo.
	The functionality of this module has been deprecated by car.py

Module [`car`](../src/car.py)
	Controls driving and steering of the car via the Car singleton class.

Module: ~~image_processing_module~~ [`image_processing`](../src/image_processing.py)\
	Processes images with OpenCV2.

Module: ~~quick_capture_module~~ [`camera`](../src/camera.py)
	Captures images from the camera to be fed into the image processing module.


# FILES

File: [`main.py`](../src/main.py)

To Do:
	1. Re-order and label imports. DONE
	2. Add more debug messages for control flow. DONE
	3. Remove deprecated or unnecessary code. DONE
	4. Move commented out code to separate cache file. DONE
	5. Find a better way of reading controller input instead of iterating. DONE
	6. Move constants to separate file. DONE
	7. Revise variable names as needed. NOT NEEDED
	8. Add more comments. DONE
	9. Also add controller option for switching to autonomous mode? DONE
	10. Resolve Polyfit warning caused by the image processing module. ??? DONE

Questions:
	1. Why the large try-catch block?
		Answer: See below.
	2. How to jump to code in except?
		Answer: When the controller is unplugged it automatically goes into autonomous mode.
	3. What is the middle portion of manual mode for?
		Answer: No longer relevant.
	4. The video recording thing doesn't work..?
		Answer: Resolved. Use VLC Media Player.

Essential Modifications:
	1. Removed unused imports: time, logging.
		Also removed `from matplotlib import pyplot as plt`.
	2. Removed commented out camera_module as cm because it appears to be deprecated.
	3. Made the try-catch system more concise.
	4. Added constants.py file.
	5. Moved manual and autonomous modes into deparate functions.
	6. Labeled video recording thing in a separate function.
	7. Created function for detecting controller inputs.
	8. Removed comments referencing deprecated camera module.
	9. Added new controls. Now requires controller to be plugged in to start.
	10. Video recording capability in autonomous.
	11. Start GPIO daemon with OS commands. This is for hardware-level GPIO control / more finegrained servo control.
	12. And more.

File: `drive_module.py` (DEPRECATED)

Deprecated. See notes for `car.py`

To Do:
	1. Clean up comments.
	2. Reorderings.
	3. Rename variables if necessary.
	4. Refine unit tests.

Questions:
	1. Wiring and ports. DONE
	2. Why disable warning?
		Answer: Possibly for former debugging purposes.
	3. Calibration setting parameters, again.
		Answer: Working on it.
	4. Video capture not working..?
		Anwer: Doesn't work.

Essential Modifications:
	1. Changed variable name dc to duty_cycle. More clear as to the intention of the code.
	2. New modeling and abstractions for physical components.

File: `steer_module.py` (DEPRECATED)

Deprecated. See notes for `car.py`

File: ~~`image_processing_module.py`~~ [`image_processing.py`](../src/image_processing.py)

To Do:
	1. Better type comments. Also apply to other modules. DONE
	2. Revise variables names if necessary. DONE
	3. Move bounds constants to constants.py. DONE

Questions:
	1. What are the calculations in the later half doing?
		Answer: See sticky notes.
	2. Potentially use 0-slope detection to determine end of path.
		Answer: Later.
	3. Why are we going faster on sharper turns?
		Answer: Turning is slower.

Essential Modifications:
	1. Added a lot of type hints. Removed the comments from the previous developer as a result, but those can be added back in later.
	2. Corrected redundant image calculation.
	3. Moved some values to the constants file.
	4. Use radians to angle conversion from the `math` module.
	5. Clarified comments. See documentation for more detailed explanation.
	6. Ignorings warning for polyfit function.
	7. Changed to use -90, 0, 90 system for steering.
	8. And more.

File: ~~`quick_capture_module.py`~~ [`camera.py`](../src/camera.py)

To Do:
1. Clean up comments. DONE
2. Rename if necessary. DONE
3. Revise class structure if necessary. DONE
4. Better utilities for debugging, as this is quite critical. DONE

Questions:
1. Why rotate image 180 degrees?
	Answer: The camera itself is flipped upside down.
2. Going faster on sharper turns?
	Answer: Lots of resistance from wheels. Part of the goal is to drive at a constant speed.

Essential Modifications:
1. Removed comment for matplotlib and other unused modules.
	NOTE: The comments left by the previous developer indicated that these may be useful in the future.
			We will refer to the commits logged on GitHub for reference should we need these.
2. Added basic test for drive.
3. Added better visual and console debug output.
4. And more.

# GENERAL

To Do:  
1. Organize workspace. DONE  
2. Create documentation file. IN PROGRESS Publish to gh-pages?!
3. Ensure files have ending newlines. DONE
4. Update .gitignore to reflect repository structure and temporary files. DONE
5. Add unit tests where appropriate to local modules. DONE
6. List versions of packages installed! DONE
7. Better joystick control? NO
8. Update VSCode. DONE

Essential Modifications:
1. Added second user nads2.
2. Set up SSH and dual use of car.  
3. Use .vscode directory.
3. Use -90, 0, 90 system.
4. Build task / launching.
5. Replaced old drive and steer modules with car module.
6. Moved old code to separate archive branch.
7. And more.

Questions:
1. How to get static type checking to detect external libraries?  
	Answer: No.

Usage notes:

1. The original user on the Raspberry Pi is "nads" with password "nads".
2. The second user is "nads2" with password "nads2".
3. Attempting to use visual tests / debugging while connected to the second user via. SSH will not work.  
	Can we set up [X forwarding?](https://en.wikipedia.org/wiki/X_Window_System) Is that worth the effort?
4. When broadcasting video output, run [`client.py`](../src/streaming_client/client.py) on target machine to view stream.
5. ~~Cannot record video while using the controller to control the car. Suspected voltage drop causes the gamepad to disconnect, forcing the program into autonomous mode.~~ You can now record video while using the controller to control the car
6. We may not have enough state information to implement model predictive control.
7. Sometimes the monitor will default to a bad resolution on boot. To correct this:
	1. Click the Raspberry Pi icon in the upper left corner.
	2. Go to Preferences --> Screen Configuration.
	3. Right click on the HDMI that appears.
	4. Select Resolution --> 1920x1080.
	5. Apply and reboot as prompted.
8. Add instructions for updating VSCode.

# ROBOT

1. If voltage is low, switch to using direct power from extension cord.
2. Steering will take power from white battery if the black one is turned off.
3. Plug the white battery into the monitor to charge.
4. To shutdown, click the Raspberry Pi icon in the upper left, navigate to logout, and then select shutdown.
	Remember to check wires and unplug as necesary for safety.
	Also command.
5. Wires.

# CAMERA

1. With OpenCV stuff, we can get the dimensions of an image with `image.shape()`.
2. The OpenCV documentation is lacking in Python. Most of it is in C++, usually with a line somewhere describing the Python embedding. The C++ documentation is still useful!
3. For some reason running in debug can cause issues with a tuple in the reverse section..?
