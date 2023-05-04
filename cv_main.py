import cv2
import asyncio
import queue
import time
import camera
from objectDetector import *
from objectDetector import *

###################################################################################
# Misc constants
###################################################################################
fieldwidth = 560
mid2mid = 178
delayms = 500

###################################################################################
# Load tensorflow inference graph
###################################################################################

modeldir = "C:/Users/black/Desktop/College_etc/ME125/foosbot/tfSourceCode/inferenceGraph/saved_model"
labelmap_path = 'C:/Users/black/Desktop/College_etc/ME125/foosbot/tfSourceCode/label_map.pbtxt'
configFile = "C:/Users/black/Desktop/College_etc/ME125/foosbot/tfSourceCode/mobilenet_v2.config"

category_index = label_map_util.create_category_index_from_labelmap(labelmap_path, use_display_name=True)
tf.keras.backend.clear_session()
model = tf.saved_model.load(modeldir)

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
			detected = objectDetector.detectObject(subque, camera.capture)
			tracker = objectTracker.initTracker(subque, detected)
		elif (detected != None and mainMsg == "t"):
			detected = objectTracker.Track(subque, tracker, detected, camera.capture)
		
		if (detected != None):
			get_player_positions(detected)
		else:
			get_player_positions([0,0])
	if mainMsg == "s":
		q.put("s")

async def init():
	#open camera
	await camera.init()

	camera.framesize(10)
	camera.contrast(2)
	camera.speffect(2)

	#discard first few frames
	asyncio.sleep_ms(200)

###################################################################################
# Main Loop
###################################################################################

#executes the main loop of the program, prints commands
def main():
	print('\r\nESP32 Ready to accept Commands\r\n')

	q = queue.Queue()
	msg = ""
	try:
		#init
		itn = init()
		detector = detect_and_track(q)
		asyncio.run(itn)
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
							detector = detect_and_track(q)
							asyncio.create_task(detector)
				opponent_active ^= 1
			elif indicatorChar =='V':
				print("Vg:" + coord[0] + "m:" + coord[1] + "v:" + vel + " \r\n")
			elif indicatorChar =='S':
				for task in asyncio.Task.all_tasks():
					task.cancel()
				exit()
	except:
		goalie_encoder_timer.deinit()
		goalie_pid_timer.deinit()
		pass

if __name__ == "__main__":
	main()
	