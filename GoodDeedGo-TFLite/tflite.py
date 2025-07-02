import numpy as np
from PIL import Image
import tensorflow as tf

LABELS = ['not_a_deed', 'planting', 'trash_pickup', 'recycling']  

interpreter = tf.lite.Interpreter(model_path="model.tflite")
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def verify_challenge_completion(photo_path):
    # Preprocess image to match your model's input
    img = Image.open(photo_path).resize((224, 224)).convert("RGB")
    input_data = np.expand_dims(np.array(img) / 255.0, axis=0).astype(np.float32)

    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

    output_data = interpreter.get_tensor(output_details[0]['index'])
    predicted_index = int(np.argmax(output_data))

    return LABELS[predicted_index]
