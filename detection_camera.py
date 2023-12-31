import numpy as np
import cv2
import os
import tensorflow as tf
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
from object_detection.builders import model_builder
from object_detection.utils import config_util

def get_frame():
  CUSTOM_MODEL_NAME = 'my_ssd_mobnet' 
  LABEL_MAP_NAME = 'label_map.pbtxt'

  paths = {
      'APIMODEL_PATH': os.path.join('Tensorflow','models'),
      'ANNOTATION_PATH': os.path.join('Tensorflow', 'workspace','annotations'),
      'CHECKPOINT_PATH': os.path.join('Tensorflow', 'workspace','models',CUSTOM_MODEL_NAME)
  }

  files = {
      'PIPELINE_CONFIG':os.path.join('Tensorflow', 'workspace','models', CUSTOM_MODEL_NAME, 'pipeline.config'),
      'LABELMAP': os.path.join(paths['ANNOTATION_PATH'], LABEL_MAP_NAME)
  }
  # Load pipeline config and build a detection model
  configs = config_util.get_configs_from_pipeline_file(files['PIPELINE_CONFIG'])
  detection_model = model_builder.build(model_config=configs['model'], is_training=False)

  # Restore checkpoint
  ckpt = tf.compat.v2.train.Checkpoint(model=detection_model)
  ckpt.restore(os.path.join(paths['CHECKPOINT_PATH'], 'ckpt-2')).expect_partial()

  @tf.function
  def detect_fn(image):
      image, shapes = detection_model.preprocess(image)
      prediction_dict = detection_model.predict(image, shapes)
      detections = detection_model.postprocess(prediction_dict, shapes)
      return detections

  category_index = label_map_util.create_category_index_from_labelmap(files['LABELMAP'])

  cap = cv2.VideoCapture(0)
  width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
  height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

  while cap.isOpened(): 
      ret, frame = cap.read()
      #frame = cv2.resize(frame,(400, 225))
      frame = cv2.resize(frame,(500, 400))
      image_np = np.array(frame)
      
      input_tensor = tf.convert_to_tensor(np.expand_dims(image_np, 0), dtype=tf.float32)
      detections = detect_fn(input_tensor)
      
      num_detections = int(detections.pop('num_detections'))
      detections = {key: value[0, :num_detections].numpy()
                    for key, value in detections.items()}
      detections['num_detections'] = num_detections

      # detection_classes should be ints.|
      detections['detection_classes'] = detections['detection_classes'].astype(np.int64)

      label_id_offset = 1
      image_np_with_detections = image_np.copy()

      # insert information text to video frame
      font = cv2.FONT_HERSHEY_SIMPLEX

      #data = detections['detection_classes']+label_id_offset
      counting_result = viz_utils.visualize_boxes_and_labels_on_image_array(
                  image_np_with_detections,
                  detections['detection_boxes'],
                  detections['detection_classes']+label_id_offset,
                  detections['detection_scores'],
                  category_index,
                  use_normalized_coordinates=True,
                  max_boxes_to_draw=5,
                  min_score_thresh=.8,
                  agnostic_mode=False)

      counting_result = str(counting_result)

    #   if(counting_result == '{}'):
    #     cv2.putText(image_np_with_detections,"...", (10, 35), font, 0.6, (0,255,255),2,cv2.FONT_HERSHEY_SIMPLEX)                       
    #   else:
    #     cv2.putText(image_np_with_detections, counting_result, (10, 35), font, 0.6, (0,255,255),2,cv2.FONT_HERSHEY_SIMPLEX)

      ret, jpeg = cv2.imencode('.jpg', image_np_with_detections)
      frame = jpeg.tobytes()
      yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
  
