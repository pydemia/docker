import os
import shutil
import numpy as np
import pandas as pd
import tensorflow as tf
import contextlib2
import math
from PIL import Image
import cv2
import functools
import modai
from modai.object_detection import model_lib
from modai.object_detection import model_hparams
from modai.object_detection import infer_object_detection
from modai.object_detection import evaluator
from modai.object_detection.utils import config_util
from modai.object_detection.utils import label_map_util
from modai.object_detection.utils import visualization_utils as vis_util
from modai.object_detection.dataset_tools import create_microorganism_tf_record
from modai.object_detection.dataset_tools import tf_record_creation_util
from modai.object_detection.builders import dataset_builder
from modai.object_detection.builders import graph_rewriter_builder
from modai.object_detection.builders import model_builder
from modai.common.utils import annotation_utils as ano_util
from modai.common.utils import file_handler
from modai.common.utils import format_converter
from modai.common.logging import logManager as Log
from modai._variables import *
from google.protobuf import text_format
from modai.object_detection import exporter
from modai.object_detection.protos import pipeline_pb2

# Get the version from the _version.py
from ._version import get_versions
__version__ = str(get_versions()['version'])


def mo_inference(model_path_n_file, input_path, output_file_path, output_image_path, progress_path_n_file, gpu_id='0'):

    log = Log.LogManager()
    logger = log.init_logger(progress_path_n_file)

    logger.info('Start Inference')

    # validate inputs
    if not os.path.exists(model_path_n_file):
        logger.error(ERR_MSG_MODEL_NOT_FOUND)
        return ERR_CD_MODEL_NOT_FOUND, ERR_MSG_MODEL_NOT_FOUND

    for path in input_path:
        if not os.path.exists(path):
            logger.error('{}:{}'.format(ERR_CD_INPUT_PATH_NOT_FOUND, path))
            return ERR_CD_INPUT_PATH_NOT_FOUND, ERR_MSG_INPUT_PATH_NOT_FOUND

    # GPU Setting
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"] = gpu_id

    # define variables
    configs = config_util.get_configs_from_pipeline_file(PIPELINE_CONFIG_PATH_N_FILE)
    model_config = configs['model']

    PATH_TO_CKPT = model_path_n_file
    NUM_CLASSES = model_config.faster_rcnn.num_classes

    # Loading label map
    label_map = label_map_util.load_labelmap(LABEL_MAP_PATH_N_FILE)
    categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
    category_index = label_map_util.create_category_index(categories)

    def detect_objects(filename, sess, detection_graph):
        #image = Image.open(filename)
        # image = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
        # image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 5)
        image = Image.open(filename)
        image_np = load_image_into_numpy_array(image)

        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
        image_np_expanded = np.expand_dims(image_np, axis=0)
        image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

        # Each box represents a part of the image where a particular object was detected.
        boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

        # Each score represent how level of confidence for each of the objects.
        # Score is shown on the result image, together with the class label.
        scores = detection_graph.get_tensor_by_name('detection_scores:0')
        classes = detection_graph.get_tensor_by_name('detection_classes:0')
        num_detections = detection_graph.get_tensor_by_name('num_detections:0')

        # Actual detection.
        (boxes, scores, classes, num_detections) = sess.run([boxes, scores, classes, num_detections], feed_dict={image_tensor: image_np_expanded})

        # Annotation of the results of a detection to xml file
        if output_file_path:
            export_path = file_handler.get_export_path_n_file(output_file_path, filename, '_result', 'xml')
            ano_util.save_boxes_and_labels_on_xml(export_path, image_np, np.squeeze(boxes), np.squeeze(classes).astype(np.int32), np.squeeze(scores), category_index, min_score_thresh=MIN_SCORE_THRESH, skip_scores=False, skip_labels=False)

        # Visualization of the results of a detection.
        image = Image.open(filename)
        image_np = load_image_into_numpy_array(image)
        vis_util.visualize_boxes_and_labels_on_image_array(image_np, np.squeeze(boxes), np.squeeze(classes).astype(np.int32), np.squeeze(scores), category_index, min_score_thresh=MIN_SCORE_THRESH, use_normalized_coordinates=True, line_thickness=2)
        if output_image_path:
            export_path = file_handler.get_export_path_n_file(output_image_path, filename, '_result', 'jpg')
            vis_util.save_image_array_as_jpg(image_np, export_path)

        return

    # Size, in inches, of the output images.
    IMAGE_SIZE = (12, 8)

    # def load_image_into_numpy_array(image):
    #     (im_width, im_height) = image.size  # PIL: image.shape, cv2.imread: image.size
    #     return np.array(image.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)
#     resp = meth(*args, **kwargs)
#   File "/tmp/skipc_microorganism_detection_model/runserver.py", line 59, in post
#     result = predict_fn(input_instances, MODEL_PATH)
#   File "/tmp/skipc_microorganism_detection_model/model.py", line 71, in predict
#     gpu_id='-1',  # '-1' for CPU
#   File "/tmp/skipc_microorganism_detection_model/modai/__init__.py", line 136, in mo_inference
#     detect_objects(filenames[i], sess, detection_graph)
#   File "/tmp/skipc_microorganism_detection_model/modai/__init__.py", line 75, in detect_objects
#     image_np = load_image_into_numpy_array(image)
#   File "/tmp/skipc_microorganism_detection_model/modai/__init__.py", line 112, in load_image_into_numpy_array
#     (im_width, im_height) = image.size  # PIL: image.shape, cv2.imread: image.size
# TypeError: 'int' object is not iterable


#   File "/tmp/skipc_microorganism_detection_model/runserver.py", line 59, in post
#     result = predict_fn(input_instances, MODEL_PATH)
#   File "/tmp/skipc_microorganism_detection_model/model.py", line 71, in predict
#     gpu_id='-1',  # '-1' for CPU
#   File "/tmp/skipc_microorganism_detection_model/modai/__init__.py", line 152, in mo_inference
#     detect_objects(filenames[i], sess, detection_graph)
#   File "/tmp/skipc_microorganism_detection_model/modai/__init__.py", line 75, in detect_objects
#     image_np = load_image_into_numpy_array(image)
#   File "/tmp/skipc_microorganism_detection_model/modai/__init__.py", line 129, in load_image_into_numpy_array
#     return np.array(image.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)
# AttributeError: 'numpy.ndarray' object has no attribute 'getdata'

    # def load_image_into_numpy_array(image):
    #     (im_width, im_height) = image.shape  # PIL: image.shape, cv2.imread: image.size
    #     return np.array(image.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)

    def load_image_into_numpy_array(image):
        # img_bgr = cv2.imread(filename, cv2.IMREAD_COLOR)
        # img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        return np.array(image)


    # Load a frozen TF model
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')

    with detection_graph.as_default():
        with tf.Session(graph=detection_graph) as sess:
            for list in input_path:
                logger.debug('inference : {}'.format(list))
                filenames = file_handler.get_all_filenames_with_ext(list,'.jpg')
                for i in range(len(filenames)):
                    detect_objects(filenames[i], sess, detection_graph)
                    if ((i+1) % PRGRESS_LOGGING_COUNT == 0) or ((i+1) == len(filenames)):
                        logger.debug('progress : {} of {}'.format(i+1, len(filenames)))

    logger.info('End Inference')

    # remove all resources
    del log

    return ERR_CD_SUCCESS, ERR_MSG_SUCCESS


def mo_train(old_model_path_n_file, new_model_path_n_file, input_seed_path_list, input_train_path_list, progress_path_n_file, hp_lr, hp_num_epoch, hp_valid_ratio, final_model, gpu_id):
    log = Log.LogManager()
    logger = log.init_logger(progress_path_n_file)

    # logging input parameters
    version = mo_get_version()
    logger.debug('[version][{}.{}]'.format(version[0], version[1]))
    logger.debug('[old_model_file][{}]'.format(old_model_path_n_file))
    logger.debug('[new_model_file][{}]'.format(new_model_path_n_file))
    logger.debug('[input_seed_path_list][{}]'.format(input_seed_path_list))
    logger.debug('[input_train_path_list][{}]'.format(input_train_path_list))
    logger.debug('[learning_rate][{}]'.format(hp_lr))
    logger.debug('[valid_ratio][{}]'.format(hp_valid_ratio))

    logger.info('Start Train')

    # define variables
    num_shards = 10

    # GPU Setting
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"] = gpu_id

    __new_model_path_n_file = new_model_path_n_file

    # validate inputs
    if old_model_path_n_file == None:
        old_model_path_n_file = CHECKPOINT_PATH_N_FILE

    if not os.path.exists(old_model_path_n_file):
        logger.error('{} {} {}'.format(ERR_CD_OLD_MODEL_NOT_FOUND, ERR_MSG_OLD_MODEL_NOT_FOUND, old_model_path_n_file))
        return ERR_CD_OLD_MODEL_NOT_FOUND, ERR_MSG_OLD_MODEL_NOT_FOUND

    if input_seed_path_list == None:
        pass
        input_seed_path_list = TRAINSET_SEED_PATH
    else:
        if not os.path.exists(input_seed_path_list):
            logger.error('{} {} {}'.format(ERR_CD_SEED_PATH_NOT_FOUND, ERR_MSG_SEED_PATH_NOT_FOUND, input_seed_path_list))
            return ERR_CD_SEED_PATH_NOT_FOUND, ERR_MSG_SEED_PATH_NOT_FOUND

    for path in input_train_path_list:
        if not os.path.exists(path):
            logger.error('{} {} {}'.format(ERR_CD_TRAIN_PATH_NOT_FOUND, ERR_MSG_TRAIN_PATH_NOT_FOUND, path))
            return ERR_CD_TRAIN_PATH_NOT_FOUND, ERR_MSG_TRAIN_PATH_NOT_FOUND

    if hp_lr == None:
        hp_lr == INIT_LEARNING_RATE

    if hp_num_epoch == None:
        hp_num_epoch == DEFAULT_NUM_EPOCH

    if hp_valid_ratio == None:
        hp_valid_ratio == DEFAULT_VALID_RATIO

    # clean train set diretories for new train
    def clean_train_set():
        file_handler.rm_all_files(TRAINSET_PATH)

    def split_train_valid(data_path_list):

        logger.debug('copy .jpg & .xml from {} to {}'.format(data_path_list, TRAINSET_PATH))

        source_path = data_path_list
        train_path = os.path.join(TRAINSET_PATH, TRAINSET_CLASSES[0])
        valid_path = os.path.join(TRAINSET_PATH, TRAINSET_CLASSES[1])

        images = file_handler.get_all_filenames_with_ext(source_path, '.jpg')
        annotations = []
        for f in images:
            filename = f.replace('.jpg', '.xml')
            annotations.append(filename)

        total_count = len(images)
        valid_count = int(total_count * hp_valid_ratio)
        train_count = total_count - valid_count
        shuffles = np.random.permutation(total_count)

        valids = shuffles[:valid_count]
        trains = shuffles[valid_count:]

        step = 0
        for idx in valids :
            step += 1
            # copy .jpg & .xml to validation
            valid_image_set.append(images[idx])
            #logger.debug('copy valid {}/{} : {}->{}'.format(step, valid_count, images[idx], valid_path))
            valid_annotation_set.append(annotations[idx])
            #logger.debug('copy valid {}/{} : {}->{}'.format(step, valid_count, annotations[idx], valid_path))

        step = 0
        for idx in trains :
            step += 1
            # copy .jpg & .xml to train
            train_image_set.append(images[idx])
            #logger.debug('copy train {}/{} : {}->{}'.format(step, train_count, images[idx], train_path))
            train_annotation_set.append(annotations[idx])
            #logger.debug('copy train {}/{} : {}->{}'.format(step, train_count, annotations[idx], train_path))

    # create tf-records
    def create_tf_records():
        # Converting xml to csv
        try:
            xml_df = format_converter.xml_to_csv(train_annotation_set)
        except Exception as e:
            logger.error('Exception!!! {}'.format(e))
            return ERR_CD_LABEL_WRONG, ERR_MSG_LABEL_WRONG
        csv_name = os.path.join(TRAINSET_PATH, '%s_labels.csv' % TRAINSET_CLASSES[0])
        xml_df.to_csv(csv_name, index=None)

        # Make tfrecord files with sharding
        images_path = os.path.join(TRAINSET_PATH, TRAINSET_CLASSES[0])
        tfrecord_name = os.path.join(TRAINSET_PATH, 'microorganism_%s.record' % (TRAINSET_CLASSES[0]))

        with contextlib2.ExitStack() as tf_record_close_stack:
            output_tfrecords = tf_record_creation_util.open_sharded_output_tfrecords(tf_record_close_stack, tfrecord_name, num_shards)
            examples = pd.read_csv(csv_name)
            grouped = create_microorganism_tf_record.split(examples, 'filename')
            for idx, group in enumerate(grouped):
                if ((idx+1) % 100 == 0) or ((idx+1) == len(grouped)):
                    logger.debug('On image %d of %d' %(idx+1, len(grouped)))
                tf_example = create_microorganism_tf_record.create_tf_example(group, images_path, LABEL_MAP_PATH_N_FILE)
                shard_idx = idx % num_shards
                output_tfrecords[shard_idx].write(tf_example.SerializeToString())

        logger.debug('Successfully created the tfrecords of {} dataset'.format(TRAINSET_CLASSES[0]))

        # Converting xml to csv
        try:
            xml_df = format_converter.xml_to_csv(valid_annotation_set)
        except Exception as e:
            logger.error('Exception!!! {}'.format(e))
            return ERR_CD_LABEL_WRONG, ERR_MSG_LABEL_WRONG
        csv_name = os.path.join(TRAINSET_PATH, '%s_labels.csv' % TRAINSET_CLASSES[1])
        xml_df.to_csv(csv_name, index=None)

        # Make tfrecord files with sharding
        images_path = os.path.join(TRAINSET_PATH, TRAINSET_CLASSES[1])
        tfrecord_name = os.path.join(TRAINSET_PATH, 'microorganism_%s.record' % (TRAINSET_CLASSES[1]))

        with contextlib2.ExitStack() as tf_record_close_stack:
            output_tfrecords = tf_record_creation_util.open_sharded_output_tfrecords(tf_record_close_stack, tfrecord_name, num_shards)
            examples = pd.read_csv(csv_name)
            grouped = create_microorganism_tf_record.split(examples, 'filename')
            for idx, group in enumerate(grouped):
                if ((idx+1) % 100 == 0) or ((idx+1) == len(grouped)):
                    logger.debug('On image %d of %d' %(idx+1, len(grouped)))
                tf_example = create_microorganism_tf_record.create_tf_example(group, images_path, LABEL_MAP_PATH_N_FILE)
                shard_idx = idx % num_shards
                output_tfrecords[shard_idx].write(tf_example.SerializeToString())

        logger.debug('Successfully created the tfrecords of {} dataset'.format(TRAINSET_CLASSES[1]))

    # frozen model
    def frozen_model(_model_dir, model_ckpt):
        pipeline_config = pipeline_pb2.TrainEvalPipelineConfig()
        with tf.gfile.GFile(PIPELINE_CONFIG_PATH_N_FILE, 'r') as f:
            text_format.Merge(f.read(), pipeline_config)
        text_format.Merge('', pipeline_config)

        checkpoint_path = os.path.join(_model_dir, model_ckpt)
        frozen_path = new_model_path_n_file #os.path.join(_model_dir, 'frozen')

        exporter.export_inference_graph('image_tensor', pipeline_config, checkpoint_path, frozen_path, input_shape=None, write_inference_graph=False)

    def train_model(_model_ckpt, epoch):

        hparams_overrides = None

        logger.debug(_model_ckpt)
        _model_dir = os.path.join(TRAIN_LOG_PATH_N_FILE,'epoch_'+str(epoch))
        if (os.path.exists(_model_dir)): file_handler.rm_all_files(_model_dir)

        config = tf.estimator.RunConfig(model_dir = _model_dir, save_checkpoints_steps=steps_of_train)

        train_and_eval_dict = model_lib.create_estimator_and_inputs(run_config=config,
                                                            hparams=model_hparams.create_hparams(hparams_overrides),
                                                            pipeline_config_path=PIPELINE_CONFIG_PATH_N_FILE,
                                                            train_steps=steps_of_train,
                                                            sample_1_of_n_eval_examples=1,
                                                            sample_1_of_n_eval_on_train_examples=5,
                                                            model_ckpt=_model_ckpt,
                                                            hp_lr=hp_lr,
                                                            batch_size=BATCH_SIZE)
        estimator = train_and_eval_dict['estimator']
        train_input_fn = train_and_eval_dict['train_input_fn']
        eval_input_fns = train_and_eval_dict['eval_input_fns']
        eval_on_train_input_fn = train_and_eval_dict['eval_on_train_input_fn']
        predict_input_fn = train_and_eval_dict['predict_input_fn']
        train_steps = train_and_eval_dict['train_steps']

        train_spec, eval_specs = model_lib.create_train_and_eval_specs(train_input_fn, eval_input_fns, eval_on_train_input_fn, predict_input_fn, train_steps, eval_on_train_data=False)

        #-------------------
        mAP = 0
        loss = 0

        logger.debug('network training........')
        box_metrics = tf.estimator.train_and_evaluate(estimator, train_spec, eval_specs[0])

        for key, value in iter(box_metrics[0].items()):
            if key == 'DetectionBoxes_Precision/mAP@.50IOU':
                mAP = value
            if key == 'loss':
                loss = value
        #-------------------
        logger.debug('network frozening.......')
        checkpoint = 'model.ckpt-' + str(steps_of_train)
        frozen_model(_model_dir, checkpoint)

        logger.info('[{}][{}][train][loss={:.2f}][mAP={:.2f}%]'.format(epoch, hp_num_epoch, loss, mAP*100))

        return (loss, mAP)

    train_image_set = []
    train_annotation_set = []
    valid_image_set = []
    valid_annotation_set = []

    logger.info('(1/4) Clean the train_set directory')
    clean_train_set()

    logger.info('(2/4) Make train & validatation data set')
    if input_seed_path_list != None:
        split_train_valid(input_seed_path_list)
    for list in input_train_path_list:	split_train_valid(list)

    logger.info('(3/4) Create tf-record files for training')
    create_tf_records()

    # train model
    steps_of_train = math.ceil(len(train_image_set) / BATCH_SIZE) # this must be fixed

    logger.info('(4/4) Train the model')
    model_ckpt = os.path.join(old_model_path_n_file, 'model.ckpt')
    best_model = 0
    best_mAP = 0
    best_loss = 1
    for epoch in range(hp_num_epoch):
        tf.reset_default_graph()
        loss, mAP = train_model(model_ckpt, epoch+1)
        model_ckpt = os.path.join(new_model_path_n_file, 'model.ckpt')
        if final_model == 'best':
            '''
            if best_mAP < mAP:
                best_mAP = mAP
                best_model = epoch+1
            '''
            if best_loss > loss:
                best_loss = loss
                best_model = epoch+1
        else:
            best_model = epoch+1
        logger.debug('best model={}, loss={}'.format(best_model, best_loss))
        if mAP > 0.98:
            break

    # frozen best model if best mode
    if final_model == 'best':
        tf.reset_default_graph()
        model_dir = os.path.join(TRAIN_LOG_PATH_N_FILE,'epoch_'+str(best_model))
        checkpoint = 'model.ckpt-' + str(steps_of_train)
        frozen_model(model_dir, checkpoint)

    logger.info('End Train')
    logger.info('[final model][{}][{}]'.format(final_model, best_model))

    # remove all resources
    del log

    return ERR_CD_SUCCESS, ERR_MSG_SUCCESS


def mo_get_version():
    version = modai.__version__.split('.')
    return int(version[0]), int(version[1])
