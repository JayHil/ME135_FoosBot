import time
import tensorflow as tf
import tensorflow_datasets as tfds
from imageAlignment import alignImage
from inferenceutils import *

# #image align NOT FUNCTIONAL

modelDir = "C:/Users/black/Desktop/College_etc/ME125/foosbot/tfSourceCode/inferenceGraph/saved_model"
labelmap_path = "C:/Users/black/Desktop/College_etc/ME125/foosbot/tfSourceCode/label_map.pbtxt"

category_index = label_map_util.create_category_index_from_labelmap(labelmap_path, use_display_name=True)
tf.keras.backend.clear_session()
model = tf.saved_model.load(modelDir)

def detectObject(q, frame):
    #get all detected objects
    output_dict = run_inference_for_single_image(model, frame)
    boxes = output_dict['detection_boxes']
    scores = output_dict['detection_scores']

    maxscore = 0.5
    maxbox = None

    #find max score object and return box
    for i in range(boxes.shape[0]):
        if (scores is None or scores[i]>maxscore):
            maxbox = boxes[i].toList()
            maxscore = scores[i]

    if (maxbox == None):
        q.put("r")
        return
    else:
        q.put("t")
        return maxbox
