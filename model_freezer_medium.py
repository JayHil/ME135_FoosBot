import tensorflow as tf
from tensorflow import keras
from tensorflow.python.framework.convert_to_constants import convert_variables_to_constants_v2
import numpy as np

#path of the directory for the frozen model
frozen_out_path = "C:/Users/black/Desktop/College_etc/ME125/foosbot/tfSourceCode/freezingExp"
# name of the .pb file
frozen_graph_filename = "frozen_graph"
#load in saved model
model_path = "C:/Users/black/Desktop/College_etc/ME125/foosbot/tfSourceCode/inferenceGraph/saved_model"
model = tf.saved_model.load(model_path)
print(model)

# Convert Keras model to ConcreteFunction
full_model = tf.function(lambda x: model(x))
full_model = full_model.get_concrete_function(
    tf.TensorSpec(model.signatures['serving_default'].inputs[0].shape.as_list(), model.signatures['serving_default'].inputs[0].dtype.name))
#full_model = full_model.get_concrete_function(
    #tf.TensorSpec(model.inputs[0].shape, model.inputs[0].dtype))
# Get frozen ConcreteFunction
frozen_func = convert_variables_to_constants_v2(full_model)
frozen_func.graph.as_graph_def()
layers = [op.name for op in frozen_func.graph.get_operations()]

print("-" * 60)
print("Frozen model layers: ")
for layer in layers:
    print(layer)
print("-" * 60)
print("Frozen model inputs: ")
print(frozen_func.inputs)
print("Frozen model outputs: ")
print(frozen_func.outputs)

# Save frozen graph to disk
tf.io.write_graph(graph_or_graph_def=frozen_func.graph,
                  logdir=frozen_out_path,
                  name=f"{frozen_graph_filename}.pb",
                  as_text=False)

# Save its text representation
tf.io.write_graph(graph_or_graph_def=frozen_func.graph,
                  logdir=frozen_out_path,
                  name=f"{frozen_graph_filename}.pbtxt",
                  as_text=True)