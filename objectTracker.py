import cv2

init = False

###################################################################################
# Functions
###################################################################################

def initTracker(q, bbox):
	tracker = cv2.TrackerCSRT_create()

	#initialize tracker bounding box from detection
	ok = tracker.init(frame, bbox)

	if not ok:
		q.put("s")

	return tracker

def Track(q, tracker, frame, bbox):
	if not init:
		q.put("s")
		return

	ok, bbox = tracker.update(frame)

	if not ok:
		q.put("r")
		init = False
		return None
