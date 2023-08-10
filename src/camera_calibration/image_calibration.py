# Import required modules
import cv2
import numpy as np
import os
import glob


# Define the dimensions of checkerboard
CHECKERBOARD = (7, 10)
filepath = "./src/camera_calibration/"

# stop the iteration when specified
# accuracy, epsilon, is reached or
# specified number of iterations are completed.
criteria = (cv2.TERM_CRITERIA_EPS +
			cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)


# Vector for 3D points
threedpoints = []

# Vector for 2D points
twodpoints = []


# 3D points real world coordinates
objectp3d = np.zeros((1, CHECKERBOARD[0]
					* CHECKERBOARD[1],
					3), np.float32)
objectp3d[0, :, :2] = np.mgrid[0:CHECKERBOARD[0],
							0:CHECKERBOARD[1]].T.reshape(-1, 2)
prev_img_shape = None


# Extracting path of individual image stored
# in a given directory. Since no path is
# specified, it will take current directory
# jpg files alone
images = glob.glob(filepath+'*.jpg')
i = 0
for filename in images:
	image = cv2.imread(filename)
	grayColor = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	# Find the chess board corners
	# If desired number of corners are
	# found in the image then ret = true
	ret, corners = cv2.findChessboardCorners(
					grayColor, CHECKERBOARD,
					cv2.CALIB_CB_ADAPTIVE_THRESH
					+ cv2.CALIB_CB_FAST_CHECK +
					cv2.CALIB_CB_NORMALIZE_IMAGE)
	print(i)

	# If desired number of corners can be detected then,
	# refine the pixel coordinates and display
	# them on the images of checker board

	if ret == True:
		
		threedpoints.append(objectp3d)

		# Refining pixel coordinates
		# for given 2d points.
		corners2 = cv2.cornerSubPix(
			grayColor, corners, (11, 11), (-1, -1), criteria)

		twodpoints.append(corners2)

		# Draw and display the corners
		image = cv2.drawChessboardCorners(image,
										CHECKERBOARD,
										corners2, ret)

	cv2.imwrite(filepath + "corners_image"+str(i)+".jpg", image)
	i+=1
	#cv2.waitKey(0)

cv2.destroyAllWindows()

h, w = image.shape[:2]


# Perform camera calibration by
# passing the value of above found out 3D points (threedpoints)
# and its corresponding pixel coordinates of the
# detected corners (twodpoints)
ret, matrix, distortion, r_vecs, t_vecs = cv2.calibrateCamera(
	threedpoints, twodpoints, grayColor.shape[::-1], None, None)


# Displaying required output
print(" Camera matrix:")
print(matrix)
np.save

print("\n Distortion coefficient:")
print(distortion)

print("\n Rotation Vectors:")
print(r_vecs)

print("\n Translation Vectors:")
print(t_vecs)

i = 0
for filename in images:
	img = cv2.imread(filename)
	h, w = img.shape[:2]
	
	newcameramtx, roi = cv2.getOptimalNewCameraMatrix(matrix, distortion, (w,h), 1, (w,h))
	dst = cv2.undistort(img, matrix, distortion, None, newcameramtx)
	#x,y,w,h = roi
	#dst = dst[y:y+h, x:x+w]

	cv2.imwrite(filepath + "corrected_image" +str(i)+ ".jpg", dst)
	i+=1
	
mean_error = 0
for i in range(len(threedpoints)):
 imgpoints2, _ = cv2.projectPoints(threedpoints[i], r_vecs[i], t_vecs[i], matrix, distortion)
 error = cv2.norm(twodpoints[i], imgpoints2, cv2.NORM_L2)/len(imgpoints2)
 mean_error += error
print( "total error: {}".format(mean_error/len(threedpoints)) )

    # dst = cv2.undistort(img, matrix, distortion, None, newcameramtx)
	# x, y, w, h = roi
	# dst = dst[y:y+h, x+w]
    # undistort