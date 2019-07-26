"""
Usage:

# Create train data:
python generate_tfrecord.py --label=<LABEL> --csv_input=<PATH_TO_ANNOTATIONS_FOLDER>/train_labels.csv  --output_path=<PATH_TO_ANNOTATIONS_FOLDER>/train.record <PATH_TO_ANNOTATIONS_FOLDER>/label_map.pbtxt

# Create test data:
python generate_tfrecord.py --label=<LABEL> --csv_input=<PATH_TO_ANNOTATIONS_FOLDER>/test_labels.csv  --output_path=<PATH_TO_ANNOTATIONS_FOLDER>/test.record  --label_map <PATH_TO_ANNOTATIONS_FOLDER>/label_map.pbtxt
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import io
import pandas as pd
import tensorflow as tf
import sys

sys.path.append("../../models/research")

from PIL import Image
from object_detection.utils import dataset_util
from collections import namedtuple, OrderedDict

flags = tf.app.flags
flags.DEFINE_string("csv_input", "", "Path to the CSV input")
flags.DEFINE_string("output_path", "", "Path to output TFRecord")
flags.DEFINE_string(
    "label_map",
    "",
    "Path to the `label_map.pbtxt` contains the <class_name>:<class_index> pairs generated by `xml_to_csv.py` or manually.",
)
# if your image has more labels input them as
# flags.DEFINE_string('label0', '', 'Name of class[0] label')
# flags.DEFINE_string('label1', '', 'Name of class[1] label')
# and so on.
flags.DEFINE_string("img_path", "", "Path to images")
FLAGS = flags.FLAGS


def split(df, group):
    data = namedtuple("data", ["filename", "object"])
    gb = df.groupby(group)
    return [
        data(filename, gb.get_group(x))
        for filename, x in zip(gb.groups.keys(), gb.groups)
    ]


def create_tf_example(group, path, label_map):
    with tf.gfile.GFile(os.path.join(path, "{}".format(group.filename)), "rb") as fid:
        encoded_jpg = fid.read()
    encoded_jpg_io = io.BytesIO(encoded_jpg)
    image = Image.open(encoded_jpg_io)
    width, height = image.size

    filename = group.filename.encode("utf8")
    image_format = b"jpg"
    # check if the image format is matching with your images.
    xmins = []
    xmaxs = []
    ymins = []
    ymaxs = []
    classes_text = []
    classes = []

    for index, row in group.object.iterrows():
        xmins.append(row["xmin"] / width)
        xmaxs.append(row["xmax"] / width)
        ymins.append(row["ymin"] / height)
        ymaxs.append(row["ymax"] / height)
        #classes_text.append(row["class"].encode("utf8"))
        classes_text.append(str(row["class"]).encode("utf8"))
        class_index = label_map.get(row["class"])
        assert (
            class_index is not None
        ), "class label: `{}` not found in label_map: {}".format(
            row["class"], label_map
        )
        classes.append(class_index)
        #classes.append(row["class"])

    tf_example = tf.train.Example(
        features=tf.train.Features(
            feature={
                "image/height": dataset_util.int64_feature(height),
                "image/width": dataset_util.int64_feature(width),
                "image/filename": dataset_util.bytes_feature(filename),
                "image/source_id": dataset_util.bytes_feature(filename),
                "image/encoded": dataset_util.bytes_feature(encoded_jpg),
                "image/format": dataset_util.bytes_feature(image_format),
                "image/object/bbox/xmin": dataset_util.float_list_feature(xmins),
                "image/object/bbox/xmax": dataset_util.float_list_feature(xmaxs),
                "image/object/bbox/ymin": dataset_util.float_list_feature(ymins),
                "image/object/bbox/ymax": dataset_util.float_list_feature(ymaxs),
                "image/object/class/text": dataset_util.bytes_list_feature(
                    classes_text
                ),
                "image/object/class/label": dataset_util.int64_list_feature(classes),
            }
        )
    )
    return tf_example


def main(_):
    writer = tf.python_io.TFRecordWriter(FLAGS.output_path)
    path = os.path.join(os.getcwd(), FLAGS.img_path)
    examples = pd.read_csv(FLAGS.csv_input)

    # Load the `label_map` from pbtxt file.
    from object_detection.utils import label_map_util

    label_map = label_map_util.load_labelmap(FLAGS.label_map)
    categories = label_map_util.convert_label_map_to_categories(
        label_map, max_num_classes=90, use_display_name=True
    )
    category_index = label_map_util.create_category_index(categories)
    label_map = {}
    for k, v in category_index.items():
        label_map[v.get("name")] = v.get("id")

    grouped = split(examples, "filename")
    for group in grouped:
        tf_example = create_tf_example(group, path, label_map)
        writer.write(tf_example.SerializeToString())

    writer.close()
    output_path = os.path.join(os.getcwd(), FLAGS.output_path)
    print("Successfully created the TFRecords: {}".format(output_path))


if __name__ == "__main__":
    tf.app.run()
