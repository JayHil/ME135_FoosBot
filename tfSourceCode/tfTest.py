import os
import re
import tensorflow as tf
import tensorflow_datasets as tfds
import matplotlib.pyplot as plt

print("TensorFlow version: {}".format(tf.__version__))
print("TensorFlow Datasets version: ",tfds.__version__)

num_classes = 1
batch_size = 16 #16
num_steps = 1500 #1500
num_eval_steps = 1000

train_record_path = 'C:/Users/black/Desktop/College etc/ME125/tfSourceCode/foosball/train.record'
test_record_path = 'C:/Users/black/Desktop/College etc/ME125/tfSourceCode/foosball/validate.record'
model_dir = 'C:/Users/black/Desktop/College etc/ME125/tfSourceCode/training'
labelmap_path = 'C:/Users/black/Desktop/College etc/ME125/tfSourceCode/label_map.pbtxt'

pipeline_config_path = 'C:/Users/black/Desktop/College etc/ME125/tfSourceCode/mobilenet_v2.config'
fine_tune_checkpoint = 'C:/Users/black/Desktop/College etc/ME125/tfSourceCode/mobilenet_v2/mobilenet_v2.ckpt-1'

print(tf.config.list_physical_devices('GPU'))

with open(pipeline_config_path) as f:
    config = f.read()

with open(pipeline_config_path, 'w') as f:

  # Set labelmap path
  config = re.sub('label_map_path: ".*?"', 
  'label_map_path: "{}"'.format(labelmap_path), config)
  
  # Set fine_tune_checkpoint path
  config = re.sub('fine_tune_checkpoint: ".*?"',
                  'fine_tune_checkpoint: "{}"'.format(fine_tune_checkpoint),
                  config)
  
  # Set train tf-record file path
  config = re.sub('(input_path: ".*?)(PATH_TO_BE_CONFIGURED/train)(.*?")', 
                  'input_path: "{}"'.format(train_record_path), config)
  
  # Set test tf-record file path
  config = re.sub('(input_path: ".*?)(PATH_TO_BE_CONFIGURED/val)(.*?")', 
                  'input_path: "{}"'.format(test_record_path), config)
  
  # Set number of classes.
  config = re.sub('num_classes: [0-9]+',
                  'num_classes: {}'.format(num_classes), config)
  
  # Set batch size
  config = re.sub('batch_size: [0-9]+',
                  'batch_size: {}'.format(batch_size), config)
  
  # Set training steps
  config = re.sub('num_steps: [0-9]+',
                  'num_steps: {}'.format(num_steps), config)
  
  f.write(config)