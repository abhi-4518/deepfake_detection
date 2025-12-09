import tensorflow as tf
import numpy as np
from PIL import Image
from app.config import FALLBACK_MODEL_PATH

class FallbackModel:
    def __init__(self, model_path: str = FALLBACK_MODEL_PATH):
        self.model_path = model_path
        try:
            self.model = tf.keras.models.load_model(model_path, compile=False)
        except Exception as e:
            print(f"Error loading fallback model from {model_path}: {e}")
            # In case the file is missing or invalid, we might want to fail or use a dummy
            # For now, we'll let it raise so we know setup is wrong, OR we catch it
            # But user wants fallback logic, so if this fails, we are in trouble.
            # I'll raise for now to be visible.
            raise e

    def predict(self, image: Image.Image) -> dict:
        # Preprocessing
        # Assuming model expects (224, 224, 3) and values [0, 1]
        target_size = (224, 224) 
        img = image.resize(target_size)
        img_array = np.array(img).astype("float32") / 255.0
        img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension

        try:
            prediction = self.model.predict(img_array, verbose=0)
            
            # Assuming output is a single probability for "AI" (binary classification)
            # or [prob_real, prob_ai]
            
            prob_ai = 0.0
            prob_real = 0.0
            
            if prediction.shape[-1] == 1:
                prob_ai = float(prediction[0][0])
                prob_real = 1.0 - prob_ai
            elif prediction.shape[-1] == 2:
                # Assuming index 0 is Real, 1 is AI, or vice versa. 
                # Without info, I will assume index 1 is AI (common convention).
                prob_real = float(prediction[0][0])
                prob_ai = float(prediction[0][1])
            else:
                 # Fallback if unknown shape, though unlikely for binary
                prob_ai = 0.5
                prob_real = 0.5

            confidence = max(prob_ai, prob_real)
            
            return {
                "prob_ai": prob_ai,
                "prob_real": prob_real,
                "confidence": confidence
            }
        except Exception as e:
            # If inference fails, return error or dummy
            print(f"Fallback model inference failed: {e}")
            return {
                "prob_ai": None,
                "prob_real": None,
                "confidence": 0.0
            }
