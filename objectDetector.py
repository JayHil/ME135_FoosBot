import cv2
import tensorflow as tf
import tensorflow_datasets as tfds
from imageAlignment import alignImage
from inferenceutils import *

#image align NOT FUNCTIONAL

modeldir = "C:/Users/black/Desktop/College etc/ME125/tfSourceCode/inferenceGraph/saved_model"
labelmap_path = 'C:/Users/black/Desktop/College etc/ME125/tfSourceCode/label_map.pbtxt'
configFile = "C:/Users/black/Desktop/College etc/ME125/tfSourceCode/mobilenet_v2.config"
label = ['Foosball']

category_index = label_map_util.create_category_index_from_labelmap(labelmap_path, use_display_name=True)
tf.keras.backend.clear_session()
model = tf.saved_model.load(modeldir)

frame = "C:/Users/black/Desktop/College etc/ME125/tensor_trainingVideo/Sequence 010002.jpg"

#object detect

image_np = load_image_into_numpy_array(frame)
output_dict = run_inference_for_single_image(model, image_np)
vis_util.visualize_boxes_and_labels_on_image_array(
    image_np,
    output_dict['detection_boxes'],
    output_dict['detection_classes'],
    output_dict['detection_scores'],
    category_index,
    instance_masks=output_dict.get('detection_masks_reframed', None),
    use_normalized_coordinates=True,
    line_thickness=8)

Image.fromarray(image_np, "RGB").show()
print(output_dict)