import cv2
import time
from imageAlignment import alignImage

#open video source and convert reference images.
s = 0
source = cv2.VideoCapture(s, cv2.CAP_DSHOW)
source_width = 1920
source_height = 1080
source.set(cv2.CAP_PROP_FRAME_WIDTH, source_width)
source.set(cv2.CAP_PROP_FRAME_HEIGHT, source_height)

#field reference for homography
#fieldRef = cv2.imread("fieldRef.jpg", cv2.IMREAD_COLOR)

trackerName = "CSRT TRACKER"

#static video source and output
#source = cv2.VideoCapture("foosballTracker.mp4");
#source.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'mp4v'))
isoTime = time.strftime('_%Y-%m-%d_%H:%M:%SZ', time.localtime())
outName = "foosballTracked" + trackerName + isoTime + ".mp4"
output = cv2.VideoWriter(outName, cv2.VideoWriter_fourcc(*'mp4v'), 10, (int(source.get(cv2.CAP_PROP_FRAME_WIDTH)), int(source.get(cv2.CAP_PROP_FRAME_HEIGHT))))

def drawRectangle(frame, bbox):
	#defines the rectangle from bounding box points
	p1 = (int(bbox[0]), int(bbox[1]))
	p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
	cv2.rectangle(frame, p1, p2, (255,0,0), 2, 1)

def drawText(frame, txt, location, color = (50,170,50)):
	cv2.putText(frame, txt, location, cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)

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

#Homography alignment.
#frame = alignImage(fieldRef, frame)

#select bbox
bbox = cv2.selectROI('Select', frame, False)
cv2.destroyWindow('Select')

if (bbox==None):
	print('No region selected')
	exit()

print(bbox)

#initialize tracker with first frame and bounding box.
ok = tracker.init(frame, bbox)

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
	output.write(frame)

source.release()
output.release()
cv2.destroyAllWindows()
