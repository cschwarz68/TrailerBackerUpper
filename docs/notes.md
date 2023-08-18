# PROJECT DOCUMENTATION
> The notes here reflect the project state as it is on branch `origin/chris`, the most up-to-date branch. Feel free to change the branch name.

Note regarding links to files: They will not work online, you must clone the repo and click on them from there.

## MODULES AND IMPORTED LIBRARIES



Library: [`inputs`](https://pypi.org/project/inputs/)  
	Inputs aims to provide cross-platform Python support for keyboards, mice and gamepads.

Library: [`cv2`](https://opencv.org/)\
	OpenCV is a library of programming functions mainly for real-time computer vision.

Library: [`numpy`](https://numpy.org)\
	The fundamental package for scientific computing with Python.

Library: [`matplotlib`](https://matplotlib.org/)\
	Matplotlib is a comprehensive library for creating static, animated, and interactive visualizations in Python. Matplotlib makes easy things easy and hard things possible.

Library: [`pigpio`](http://abyz.me.uk/rpi/pigpio/)\
	This package provides a Python module to control the GPIO on a Raspberry Pi.


Module [`truck`](../src/truck.py)\
	Controls driving and steering of the car via the Truck singleton class.

Module: [`image_processing`](../src/image_processing.py)\
	Processes images with OpenCV2.

Module: [`camera`](../src/camera.py)\
	Captures images from the camera to be fed into the image processing module.

Module: [`gpio`](../src/gpio.py)\
This module controls DC Motors and Servos. It is imported by the `truck` module. If you are about to use something in this module directly, check `truck` first, as it is pretty complete.

Module: [`gamepad`](../src/gamepad.py)\
`gamepad` provides an interface for a connected x-input gamepad/controller.

Module: [`image_utils`](../src/image_utils.py)\
This module contains general image processing functions. Unlike those in image_processing, these do not do any calculations regarding control of the vehicle.

Module: [`model.py`](../src/model.py)\
This module is mostly a relic from before my time. There is a hope to train a neural network to control the robot one day, and this code is for that.

Modules: [`mpc.py`](../src/mpc.py) and [`mpc_test.py`](../src/mpc_test.py)\
`mpc.py` is an implementation of model predictive control using live state information from the vehicle. `mpc_test.py` is being used for basic testing. Functionality should eventually be moved and `mpc_test` deprecated/removed.

Module: [`speedometer.py`](../src/speedometer.py)\
This module calculates the speed of the car by looking at a yellow marker on the trailer wheel. A wheel encoder would be better and easier.

Module:[`state_informer.py`](../src/state_informer.py)\
This module is responsible for calculating and providing all required state information for implementing model predictive control.


# THINGS TO DO

File: [`main.py`](../src/main.py)

To Do:
1. Implement model predictive control
2. File is very big. Clean up.

Elaboration: \
Model predictive control has been implemented in Python by Dr. Schwarz in 
[`trailer1.py`](../src/model_predictive_control/trailer1.py).
 In [`mpc.py`](../src/mpc.py), this has been adapted to use real information
 about the state of the truck and trailer system.
 The file [`mpc_test.py`](../src/mpc_test.py) contains is a preliminary attempt
 at actually using the model to control the vehicle. This should eventually be
 done in the main loop of the program. See documentation for `image_processing`
 for the current obstacles to doing this.


File: [`image_processing.py`](../src/image_processing.py)

To Do:
1. Image processing has been left almost unchanged since before we started trying
to handle the problem of reverse autonomous driving.

Elaboration: \
For forward driving, one can fit straight lines over the detected lanes
and navigate quite well, even in sharp turns. However, In reverse driving, we must look further because the trailer is up ahead of the truck. This causes two main problems:
1. Seeing the lane well
2. Straight lines are not a good approximation of curves anymore

I've attempted to use perspective transforms and fisheye distortion correction to get a better view of the lane at a distance. This seems to work quite well, but when put into the image processing pipeline, performance becomes far too slow. I believe this is because of the additional processing requirement of performing these image transformations, and also because a much higher image resolution is needed to get an acceptable reslution following the transformations. See [`camera_calibration`](../src/camera_calibration/src/)'s files for more specific information (these features are in `camera_calibration` as I was still experimenting with them and didn't actually put them in `image_processing`).



File: [`state_informer.py`](../src/state_informer.py)

To Do:
1. The primary issue with the system is lane detection in reverse driving, as touched on in the above section regarding `image_processing.py`.
2. Currently, the frame line of code which performs the transformations and undistortions is commented out, as it slows performance too much. I think making this work effectively is the key to fully implementing the model predictive control.

Other files not mentioned here are mostly complete and ok. See documentation in each file for specific information.



# USAGE INSTRUCTIONS

1. Connect to Raspberry Pi via SSH. [VSCode SSH Instructions Here](https://code.visualstudio.com/docs/remote/ssh)
2. Ensure gamepad is plugged in.
2. Run `main.py`
3. The program will start in manual control mode.
4. Controls are as follows:

		Left Stick: Steering Control
		Right Trigger: Forward Acceleration
		Left Trigger: Reverse Acceleration
		X: Transition to forward autonomous mode
		Y: Transition to reverse autonomous mode
		START: Confirm transition.
		A: Enable/disable recording (this feature is functional in main branch, but not in origin/chris)
		SELECT: Enable/disable streaming (streaming).

		NOTE: In main branch, streaming only works in autonomous modes, in chris branch, streaming works in all modes, and is always active (no toggling with SELECT)

		B: If in autonomous mode, B will return the vehicle to manual control. If in manual mode, B will shutdown the program.

5. Enter Ctrl+C into the terminal to cleanup and shutdown the program as an alternative to using the controller.

# LESS IMPORTANT FEATURES THAT COULD BE COOL
1. Streaming to HTML page
2. X-forwarding for use of display-dependant functions.
3. Second camera so forward and reverse autonomous can actually both be used.
4. Ability to change streaming image live. (I'm thinking maybe press LB and RB to cycle between streamed windows.) I found that having to go into the code to change the streamed image slowed debugging a lot.
5. Keyboard contol using [`curses`](https://docs.python.org/3/howto/curses.html) as an alternative to gamepad control. (+ other terminal improvements from `curses`)
6. WHEEL ENCODER!!!!!!!!!!!!
7. Start trying to get a neural network trained again. Now that camera can operate in manual control mode, a human could be used as the training data.
