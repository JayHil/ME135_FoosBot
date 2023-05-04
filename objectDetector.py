import cv2
import time
import tensorflow as tf
import tensorflow_datasets as tfds
from imageAlignment import alignImage
from inferenceutils import *

#image align NOT FUNCTIONAL

modeldir = "C:/Users/black/Desktop/College etc/ME125/foosbot/tfSourceCode/inferenceGraph/saved_model"
labelmap_path = 'C:/Users/black/Desktop/College etc/ME125/foosbot/tfSourceCode/label_map.pbtxt'
configFile = "C:/Users/black/Desktop/College etc/ME125/foosbot/tfSourceCode/mobilenet_v2.config"
label = ['Foosball']

category_index = label_map_util.create_category_index_from_labelmap(labelmap_path, use_display_name=True)
tf.keras.backend.clear_session()
model = tf.saved_model.load(modeldir)

frame = "C:/Users/black/Desktop/College etc/ME125/tensor_trainingVideo/Sequence 010002.jpg"

#object detect
start = time.time()
image_np = load_image_into_numpy_array(frame)
output_dict = run_inference_for_single_image(model, image_np)
end = time.time() - start

print("latency: " + str(end))

print(output_dict['detection_boxes'])

Image.fromarray(image_np, "RGB").show()