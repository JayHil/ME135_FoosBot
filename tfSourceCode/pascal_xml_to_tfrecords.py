# coding: utf-8
# Converting LabelImg Annotated XML(in Pascal VOC format) into tfrecords.
import os
import io
import PIL
import glob
import random
import hashlib
import tensorflow as tf
from xml.etree import ElementTree as etree
from object_detection.utils import label_map_util, dataset_util

def dict_to_tf_example(data,
                       label_map_dict,
                       ignore_difficult_instances=False):


    """Convert XML derived dict to tf.Example proto.

    Notice that this function normalizes the bounding box coordinates provided
    by the raw data.

    Args:
      data: dict holding PASCAL XML fields for a single image (obtained by
        running dataset_util.recursive_parse_xml_to_dict)
      dataset_directory: Path to root directory holding PASCAL dataset
      label_map_dict: A map from string label names to integers ids.
      ignore_difficult_instances: Whether to skip difficult instances in the
        dataset  (default: False).
      image_subdirectory: String specifying subdirectory within the
        PASCAL dataset directory holding the actual image data.

    Returns:
      example: The converted tf.Example.

    Raises:
      ValueError: if the image pointed to by data['filename'] is not a valid JPEG
    """
    img_path = data['path']
    with tf.io.gfile.GFile(img_path, 'rb') as fid:
        encoded_jpg = fid.read()
    encoded_jpg_io = io.BytesIO(encoded_jpg)
    image = PIL.Image.open(encoded_jpg_io)
    if image.format != 'JPEG':
        raise ValueError('Image format not JPEG')
    key = hashlib.sha256(encoded_jpg).hexdigest()

    width = int(data['size']['width'])
    height = int(data['size']['height'])

    xmin = []
    ymin = []
    xmax = []
    ymax = []
    classes = []
    classes_text = []
    truncated = []
    poses = []
    difficult_obj = []
    if 'object' in data:
        for obj in data['object']:
            difficult = bool(int(obj['difficult']))
            if ignore_difficult_instances and difficult:
                continue
            difficult_obj.append(int(difficult))

            xmin.append(float(obj['bndbox']['xmin']) / width)
            ymin.append(float(obj['bndbox']['ymin']) / height)
            xmax.append(float(obj['bndbox']['xmax']) / width)
            ymax.append(float(obj['bndbox']['ymax']) / height)
            classes_text.append(obj['name'].encode('utf8'))
            classes.append(label_map_dict[obj['name']])
            truncated.append(int(obj['truncated']))
            poses.append(obj['pose'].encode('utf8'))

    example = tf.train.Example(features=tf.train.Features(feature={
        'image/height': dataset_util.int64_feature(height),
        'image/width': dataset_util.int64_feature(width),
        'image/filename': dataset_util.bytes_feature(
            data['filename'].encode('utf8')),
        'image/source_id': dataset_util.bytes_feature(
            data['filename'].encode('utf8')),
        'image/key/sha256': dataset_util.bytes_feature(key.encode('utf8')),
        'image/encoded': dataset_util.bytes_feature(encoded_jpg),
        'image/format': dataset_util.bytes_feature('jpeg'.encode('utf8')),
        'image/object/bbox/xmin': dataset_util.float_list_feature(xmin),
        'image/object/bbox/xmax': dataset_util.float_list_feature(xmax),
        'image/object/bbox/ymin': dataset_util.float_list_feature(ymin),
        'image/object/bbox/ymax': dataset_util.float_list_feature(ymax),
        'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
        'image/object/class/label': dataset_util.int64_list_feature(classes),
        'image/object/difficult': dataset_util.int64_list_feature(difficult_obj),
        'image/object/truncated': dataset_util.int64_list_feature(truncated),
        'image/object/view': dataset_util.bytes_list_feature(poses),
    }))
    return example

def xml_to_tf_example(xml_path, label_map_dict):
    with tf.io.gfile.GFile(xml_path, 'r') as fid:
        xml_str = fid.read()
    xml = etree.fromstring(xml_str)
    data = dataset_util.recursive_parse_xml_to_dict(xml)['annotation']

    tf_example = dict_to_tf_example(data, label_map_dict,ignore_difficult_instances=True)
    return tf_example


def convert_to_tfrecords(annotation_dir, label_map_path, train_records_file, val_records_file, train_val_split = 0.8):

    xml_files = glob.glob(os.path.join(annotation_dir, "*.xml"))
    random.shuffle(xml_files)

    total = len(xml_files)
    split_pos = int(len(xml_files) * 0.8)
    print("Total examples: {}, train examples: {}.".format(total, split_pos))

    label_map_dict = label_map_util.get_label_map_dict(label_map_path)
    with tf.io.TFRecordWriter(train_records_file) as train_writer, tf.io.TFRecordWriter(val_records_file) as val_writer:
        for i, xml_path in enumerate(xml_files):
            tf_example = xml_to_tf_example(xml_path, label_map_dict)
            writer = train_writer if i < split_pos else val_writer
            writer.write(tf_example.SerializeToString())

if __name__ == '__main__':
    train_records_file = "C:/Users/black/Desktop/College etc/ME125/tfSourceCode/foosball/train.record"
    val_records_file = "C:/Users/black/Desktop/College etc/ME125/tfSourceCode/foosball/validate.record"
    label_map_path = "C:/Users/black/Desktop/College etc/ME125/tfSourceCode/label_map.pbtxt"
    annotated_images_dir = "C:/Users/black/Desktop/College etc/ME125/tfSourceCode/foosball/annotated"
    convert_to_tfrecords(annotated_images_dir, label_map_path, train_records_file, val_records_file)