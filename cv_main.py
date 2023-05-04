import cv2
import uasyncio
import queue
import utime
import camera

###################################################################################
# Misc constants
###################################################################################
fieldwidth = 560
mid2mid = 178
delayms = 500

###################################################################################
# Load tensorflow inference graph
###################################################################################

modeldir = "C:/Users/black/Desktop/College etc/ME125/foosbot/tfSourceCode/inferenceGraph/saved_model"
labelmap_path = 'C:/Users/black/Desktop/College etc/ME125/foosbot/tfSourceCode/label_map.pbtxt'
configFile = "C:/Users/black/Desktop/College etc/ME125/foosbot/tfSourceCode/mobilenet_v2.config"

category_index = label_map_util.create_category_index_from_labelmap(labelmap_path, use_display_name=True)
tf.keras.backend.clear_session()
model = tf.saved_model.load(modeldir)

###################################################################################
# Functions
###################################################################################

def get_player_positions(centroid):
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
	while(q != ""):
		
	await 

async def init():
	#open camera
	await camera.init()

	camera.framesize(10)
	camera.contrast(2)
	camera.speffect(2)

	#discard first few frames
	uasyncio.sleep_ms(200)

###################################################################################
# Main Loop
###################################################################################

#executes the main loop of the program, prints commands
def main():
	print('\r\nESP32 Ready to accept Commands\r\n')

	que = asyncio.Queue()

	try:
		#init
		itn = init()
		detector = detect_and_track()
	    uasync.run(itn)
	    while(1):
	        command=input('')
	        indicatorChar=command[0]

	        if indicatorChar == 'T':
	            if opponent_active == 1:
	                print("TOpponent Disabled \r\n")
	            else:
	                print("TOpponent Enabled \r\n")
	                uasync.create_task(detector)
	            opponent_active ^= 1
	        elif indicatorChar =='V':
	        	print("Vg:" + coord[0] + "m:" + coord[1] + "v:" + vel + " \r\n")
	except:
	    goalie_encoder_timer.deinit()
	    goalie_pid_timer.deinit()
	    pass

if __name__ == "__main__":
    main()
	