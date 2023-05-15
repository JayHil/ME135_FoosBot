import cv2
import time
import numpy as np
import tensorflow as tf
import tensorflow_datasets as tfds
from inferenceutils import *

###################################################################################
# Initialize tensorflow model
###################################################################################

modelDir = "C:/Users/gheis/Desktop/Administrative/College_etc/FoosbotME135/ME135_FoosBot/tfSourceCode/inferenceGraph/saved_model"
labelmap_path = "C:/Users/gheis/Desktop/Administrative/College_etc/FoosbotME135/ME135_FoosBot/tfSourceCode/label_map.pbtxt"

category_index = label_map_util.create_category_index_from_labelmap(labelmap_path, use_display_name=True)
tf.keras.backend.clear_session()
model = tf.saved_model.load(modelDir)

###################################################################################
# Important Metrics
###################################################################################

#camera resolution
source_width = 1920
source_height = 1080
#set the index of the camera to open
s = 0
#name of the console window
windowName = 'Camera Preview'
trackerName = "CSRT TRACKER"

###################################################################################
# Open source and configure
###################################################################################

def initializeCamera():
	#open video source
	source = cv2.VideoCapture(s, cv2.CAP_DSHOW)

	#sleep through camera start frames
	time.sleep(2)

	#set source resolution
	source.set(cv2.CAP_PROP_FRAME_WIDTH, source_width)
	source.set(cv2.CAP_PROP_FRAME_HEIGHT, source_height)

	#set up console window
	cv2.namedWindow(windowName)
	cv2.resizeWindow(windowName, int(source_width/2), int(source_height/2))

	ok = False
	count = 0

	while not ok:
		if (count == 5):
			print("couldn't retrieve frames")
			return False, None
		ok = source.grab()
		if not ok:
			print("couldn't grab image from camera, retrying")
			time.sleep_ms(200)
			count+=1

	print("camera initialized")

	return True, source

###################################################################################
# Display functions
###################################################################################

def drawRectangle(frame, bbox):
	#defines the rectangle from bounding box points
	p1 = (int(bbox[0]), int(bbox[1]))
	p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
	cv2.rectangle(frame, p1, p2, (255,0,0), 2, 1)

def drawText(frame, txt, location, color = (50,170,50)):
	cv2.putText(frame, txt, location, cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)

###################################################################################
# Object Tracking
###################################################################################

#takes current frame and updates the tracker, returns a bool for success or failure and the updated frame
def track(frame, bbox):
    #update tracker with new frame
    ok, bbox = tracker.update(frame)
   	#draw bounding box
    if ok:
    	drawRectangle(frame, bbox)
    	return (True, frame)
    else:
    	drawText(frame, "Tracking failure", (80,140), (0,0,255))
    	return (False, frame)

###################################################################################
# Detect foosball
###################################################################################

def detect(frame):
	#get all detected objects
	output_dict = run_inference_for_single_image(model, frame)
	boxes = output_dict['detection_boxes']
	scores = output_dict['detection_scores']

	bbox = None
	minscore = 0.5

	#find max score object and return box
	for i in range(boxes.shape[0]):
	    if (scores is None or scores[i]>=minscore):
	    	bbox = (int(boxes[i][1] * source_width), int(boxes[i][0] * source_height), int(boxes[i][3] * source_width), int(boxes[i][2] * source_height))
	    	minscore = scores[i]

	if (bbox == None or bbox == []):
		return (False, None)
	return (True, bbox)

###################################################################################
# Main Loop
###################################################################################

def main():

	#initialize camera
	ok, source = initializeCamera()
	if not ok:
		print("couldn't start camera stream")
		exit()

	#Initialize a new tracker
	tracker = cv2.TrackerCSRT_create()
	tracking = False
	bbox = None
	while cv2.waitKey(1) != 27:
		#timer for fps counter
		timer = cv2.getTickCount()

		ok, frame = source.read()

		#currently broken image alignment
		#frame = alignImage(fieldRef, frame)

		#try to detect the ball if
		if ok and not tracking:
			ok, bbox = detect(frame)
		elif not tracking:
			drawText(frame, "DETECT FAIL", (80,140), (0,0,255))

		if (ok and bbox != None):
			#initialize tracker with first frame and bounding box.
			ok = tracker.init(frame, bbox)
			if ok:
				tracking = True
				ok, frame = track(frame)
			else:
				tracking = False
				drawText(frame, "INIT FAIL", (80,140), (0,0,255))

		#Write the tracker type and fps to frame
		drawText(frame, trackerName, (80, 60))
		fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)
		drawText(frame, "FPS " + str(int(fps)), (80, 100))

		#display final frame
		cv2.imshow(windowName, frame)

	source.release()
	cv2.destroyAllWindows()

if __name__ == "__main__":
	main()
