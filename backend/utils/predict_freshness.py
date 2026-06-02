import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import custom_object_scope
from utils.preprocess import preprocess_image
from config import Config

# =====================================================================
# MONKEY PATCH
# =====================================================================
try:
    import keras.src.engine.functional as keras_functional
    original_process_node = keras_functional.process_node

    def patched_process_node(node, layer_dict, dictionary):
        if hasattr(node, 'input_tensors'):
            inputs = node.input_tensors
            if isinstance(inputs, str):
                node.input_tensors = [inputs]
        return original_process_node(node, layer_dict, dictionary)

    keras_functional.process_node = patched_process_node
except Exception:
    pass

try:
    from keras.src.engine import node as keras_node
    original_flat_input_ids = keras_node.Node.flat_input_ids.fget

    def patched_flat_input_ids(self):
        try:
            return original_flat_input_ids(self)
        except AttributeError:
            return []

    keras_node.Node.flat_input_ids = property(patched_flat_input_ids)
except Exception:
    pass

try:
    import tensorflow as tf
    original_as_list = tf.TensorShape.as_list

    def patched_as_list(self):
        try:
            return original_as_list(self)
        except Exception:
            return []

    tf.TensorShape.as_list = patched_as_list
except Exception:
    pass

try:
    import keras.src.engine.input_layer as keras_input_layer
    original_input_from_config = keras_input_layer.InputLayer.from_config

    @classmethod
    def patched_from_config(cls, config):
        if 'batch_shape' in config:
            batch_shape = config.pop('batch_shape')
            if batch_shape and len(batch_shape) > 1:
                config['input_shape'] = batch_shape[1:]
        config.pop('optional', None)
        return original_input_from_config(config)

    keras_input_layer.InputLayer.from_config = patched_from_config
except Exception:
    pass

try:
    from keras.src.engine import base_layer
    original_base_from_config = base_layer.Layer.from_config

    @classmethod
    def patched_base_from_config(cls, config):
        config.pop('quantization_config', None)
        return original_base_from_config.__func__(cls, config)

    base_layer.Layer.from_config = patched_base_from_config
except Exception:
    pass

class FakeDTypePolicy:
    def __init__(self, *args, **kwargs):
        config = kwargs.get('config', {})
        self.name = config.get('name', 'float32') if isinstance(config, dict) else 'float32'
    def __getattr__(self, name):
        return 'float32'
# =====================================================================

_model = None

def get_model():
    global _model
    if _model is None:
        with custom_object_scope({'DTypePolicy': FakeDTypePolicy}):
            _model = load_model(Config.FRESHNESS_MODEL_PATH, compile=False)
    return _model

def predict_freshness(img_path):
    model = get_model()
    processed_image = preprocess_image(img_path)
    raw_score = float(model.predict(processed_image)[0][0])
    if raw_score >= 0.5:
        freshness = "Fresh"
        confidence = raw_score
    else:
        freshness = "Non-Fresh"
        confidence = 1.0 - raw_score
    return freshness, confidence