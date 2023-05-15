import cv2
import asyncio
import queue
import time
#import camera
from objectDetector import *
from objectTracker import *

###################################################################################
# Misc constants
###################################################################################
fieldwidth = 560
mid2mid = 178
delayms = 500
source = None
source_width = 1920
source_height = 1080

###################################################################################
# Functions
###################################################################################

def get_player_positions(bbox):
	#center of bound box
	centroid = [(bbox[0] + bbox[2])/2, (bbox[1] + bbox[3])/2]
	#goalie and midfield 
	g_x = 0
	m_x = 0

	#calculate the closest player to the ball and add offset
	#right field, move center to left
	if (centroid[0] > mid2mid):
		m_x = - fieldwidth/2 + centroid[0]
	#left field, move center to right
	elif (centroid[0] < -mid2mid):
		m_x = fieldwidth/2 + centroid[0]
	#move middle absolute
	else:
		m_x = centroid[0]

	coords = [[g_x,centroid[1]],[m_x,centroid[1]]]
	return coords, velocity

async def detect_and_track(q):
	subque = queue.Queue()
	mainMsg = ""
	detected = None
	tracker = None
	while(mainMsg != "s"):
		if not subque.empty():
			mainMsg = subque.get()
		if (detected == None or mainMsg == "r"):
			detected = objectDetector.detectObject(subque, source.read())
			tracker = objectTracker.initTracker(subque, source.read(), detected)
		elif (detected != None and mainMsg == "t"):
			detected = objectTracker.Track(subque, tracker, detected, source.read())
		
		if (detected != None):
			get_player_positions(detected)
		else:
			get_player_positions([0,0])
	if mainMsg == "s":
		q.put("s")

def init():
	# #open camera
	# await camera.init()

	# camera.framesize(10)
	# camera.contrast(2)
	# camera.speffect(2)

	# #discard first few frames
	# asyncio.sleep_ms(200)

	#cv2 version
	source = cv2.VideoCapture(0, cv2.CAP_DSHOW)
	time.sleep(1)
	ok, frame = source.read()

	if not ok:
		print('cannot read the video')

	source.set(cv2.CAP_PROP_FRAME_WIDTH, source_width)
	source.set(cv2.CAP_PROP_FRAME_HEIGHT, source_height)

###################################################################################
# Main Loop
###################################################################################

async def main():
	print('\r\nESP32 Ready to accept Commands\r\n')

	q = queue.Queue()
	msg = ""
	try:
		#init
		init()
		detector = asyncio.create_task(detect_and_track(q))
		while(msg != "s"):
			if not q.empty():
				msg = q.get()

			command=input('')
			indicatorChar=command[0]

			if indicatorChar == 'T':
				if opponent_active == 1:
					print("TOpponent Disabled \r\n")
					if (detector != None):
						detector.cancel()
						detector = None
					else:
						print("TOpponent Enabled \r\n")
					if (detector.iscoroutine()):
						if (detector.done() or detector.cancelled()):
							detector = asyncio.create_task(detect_and_track(q))
							detector

				opponent_active ^= 1
			elif indicatorChar =='V':
				print("Vg:" + coord[0] + "m:" + coord[1] + "v:" + vel + " \r\n")
			elif indicatorChar =='S':
				for task in asyncio.Task.all_tasks():
					task.cancel()
				exit()
	except:
		pass

if __name__ == "__main__":
	asyncio.run(main())
	