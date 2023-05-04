import cv2
import time
import time
import tensorflow as tf
import tensorflow_datasets as tfds
from inferenceutils import *

###################################################################################
# Initialize model and detection
###################################################################################

modelDir = "C:/Users/black/Desktop/College_etc/ME125/foosbot/tfSourceCode/inferenceGraph/saved_model"
labelmap_path = "C:/Users/black/Desktop/College_etc/ME125/foosbot/tfSourceCode/label_map.pbtxt"

category_index = label_map_util.create_category_index_from_labelmap(labelmap_path, use_display_name=True)
tf.keras.backend.clear_session()
model = tf.saved_model.load(modelDir)

###################################################################################
# Open source and configure
###################################################################################

#open video source
s = 0
source = cv2.VideoCapture(s, cv2.CAP_DSHOW)
source_width = 1920
source_height = 1080
source.set(cv2.CAP_PROP_FRAME_WIDTH, source_width)
source.set(cv2.CAP_PROP_FRAME_HEIGHT, source_height)

trackerName = "CSRT TRACKER"

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
# Initialize Tracker
###################################################################################

#Create a new tracker
tracker = cv2.TrackerCSRT_create()

#set up console window
windowName = 'Camera Preview'
cv2.namedWindow(windowName)
cv2.resizeWindow(windowName, int(source_width/2), int(source_height/2))

#read in first frame to initialize tracker
time.sleep(2)
ok, frame = source.read()

if not ok:
    print('cannot read the video')
    exit()

###################################################################################
# Detect foosball
###################################################################################

#get all detected objects
output_dict = run_inference_for_single_image(model, frame)
boxes = output_dict['detection_boxes']
scores = output_dict['detection_scores']

maxscore = 0
bbox = None

#find max score object and return box
for i in range(boxes.shape[0]):
    if (scores is None or scores[i]>=maxscore):
        bbox = boxes[i]
        maxscore = scores[i]

bbox = bbox.astype(int)

#initialize tracker with first frame and bounding box.
ok = tracker.init(frame, bbox)

###################################################################################
# Main Loop
###################################################################################

#main loop through frames need break points for manual interrupts and errors/priority interrupts
while cv2.waitKey(1) != 27:
	ok = source.grab()
	if not ok:
		break

	source.retrieve(frame)
	#currently broken image alignment
	#frame = alignImage(fieldRef, frame)
	
	#timer
	timer = cv2.getTickCount()

	#update tracker with new frame
	ok, bbox = tracker.update(frame)

	#draw bounding box
	if ok:
		drawRectangle(frame, bbox)
	else:
		drawText(frame, "Tracking failure detected", (80,140), (0,0,255))

	#Write the tracker type and fps to frame
	drawText(frame, trackerName, (80, 60))
	fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)
	drawText(frame, "FPS " + str(int(fps)), (80, 100))

	#display final frame
	cv2.imshow(windowName, frame)

source.release()
cv2.destroyAllWindows()
