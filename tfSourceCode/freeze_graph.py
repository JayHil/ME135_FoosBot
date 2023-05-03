import tensorflow as tf
from tensorflow import keras
import tensorflow_hub as hub
from tensorflow.python.framework.convert_to_constants import convert_variables_to_constants_v2
import numpy as np

from freeze_utils import wrap_frozen_graph


def main():

    pb_model_dir = "C:/Users/black/Desktop/College etc/ME125/tfSourceCode/inferenceGraph/saved_model"
    h5_model = "keras_model.h5"

    model = tf.saved_model.load(pb_model_dir)

    model = tf.keras.Sequential([hub.KerasLayer("saved_model", trainable=True),
        tf.keras.layers.Dense(10, activation='softmax')
    ])

    print(model.summary())

    # Convert Keras model to ConcreteFunction
    full_model = tf.function(lambda x: model(x))
    full_model = full_model.get_concrete_function(
        x=tf.TensorSpec(model.inputs[0].shape, model.inputs[0].dtype))

    # Get frozen ConcreteFunction
    frozen_func = convert_variables_to_constants_v2(full_model)
    frozen_func.graph.as_graph_def()

    layers = [op.name for op in frozen_func.graph.get_operations()]
    print("-" * 50)
    print("Frozen model layers: ")
    for layer in layers:
        print(layer)

    print("-" * 50)
    print("Frozen model inputs: ")
    print(frozen_func.inputs)
    print("Frozen model outputs: ")
    print(frozen_func.outputs)

    # Save frozen graph from frozen ConcreteFunction to hard drive
    tf.io.write_graph(graph_or_graph_def=frozen_func.graph,
                      logdir="C:/Users/black/Desktop/College etc/ME125/tfSourceCode/inferenceGraph",
                      name="frozen_graph.pb",
                      as_text=False)

if __name__ == "__main__":

    main()
