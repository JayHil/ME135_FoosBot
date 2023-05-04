import cv2
import utime
from imageAlignment import alignImage

###################################################################################
# Functions
###################################################################################

def initTracker():
	tracker = cv2.TrackerCSRT_create()

	#bounding box from detection

	ok = tracker.init(frame, bbox)

def Track():
