import logging
import traceback
from PIL import Image

from app.models.primary_model import PrimaryModel
from app.models.fallback_model import FallbackModel
from app.config import PRIMARY_CONFIDENCE_THRESHOLD

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DetectionService:
    def __init__(self):
        logger.info("Initializing DetectionService...")
        self.primary_model = None
        self.fallback_model = None
        self.primary_error = None
        self.fallback_error = None
        
        try:
            self.primary_model = PrimaryModel()
            logger.info("Primary model loaded successfully.")
        except Exception as e:
            self.primary_error = str(e)
            logger.error(f"Failed to load primary model: {e}")
            logger.error(traceback.format_exc())

        try:
            self.fallback_model = FallbackModel()
            logger.info("Fallback model loaded successfully.")
        except Exception as e:
            self.fallback_error = str(e)
            logger.error(f"Failed to load fallback model: {e}")
            logger.error(traceback.format_exc())

    async def detect_image(self, image: Image.Image) -> dict:
        response = {
            "primary": {"status": "skipped", "confidence": None},
            "fallback": {"status": "skipped", "used": False},
            "final_decision": {}
        }

        # 1. Try Primary Model
        primary_success = False
        if self.primary_model:
            try:
                primary_result = self.primary_model.predict(image)
                response["primary"] = {
                    "status": "success",
                    **primary_result
                }
                
                # Check confidence
                if primary_result["confidence"] >= PRIMARY_CONFIDENCE_THRESHOLD:
                    primary_success = True
                    # Set final decision from primary
                    self._set_final_decision(response, primary_result, "primary")
                else:
                    logger.info(f"Primary model low confidence: {primary_result['confidence']:.4f} < {PRIMARY_CONFIDENCE_THRESHOLD}")
            
            except Exception as e:
                logger.error(f"Primary model inference failed: {e}")
                response["primary"]["status"] = "error"
                response["primary"]["error_message"] = str(e)
        else:
            response["primary"]["status"] = "not_loaded"
            response["primary"]["error_message"] = self.primary_error

        # 2. Fallback if needed
        if not primary_success:
            logger.info("Engaging fallback model...")
            response["fallback"]["used"] = True
            
            fallback_ran_successfully = False
            
            if self.fallback_model:
                try:
                    fallback_result = self.fallback_model.predict(image)
                    response["fallback"].update({
                        "status": "success",
                        **fallback_result
                    })
                    
                    self._set_final_decision(response, fallback_result, "fallback")
                    fallback_ran_successfully = True
                except Exception as e:
                     logger.error(f"Fallback model inference failed: {e}")
                     response["fallback"]["status"] = "error"
                     response["fallback"]["error_message"] = str(e)
            else:
                 response["fallback"]["status"] = "not_loaded"
                 response["fallback"]["error_message"] = self.fallback_error
            
            # If fallback didn't run effectively, revert to primary if it was successful (even if low confidence)
            if not fallback_ran_successfully:
                if response["primary"]["status"] == "success":
                    logger.info("Fallback unavailable/failed, reverting to primary result despite low confidence.")
                    primary_data = response["primary"]
                    # Reconstruct result object for helper
                    # prob_ai/real are in the dict
                    self._set_final_decision(response, primary_data, "primary (low confidence fallback)")
                else:
                    # Both failed
                     response["final_decision"] = {
                        "label": "unknown",
                        "prob_ai": 0.0,
                        "prob_real": 0.0,
                        "source": "none"
                    }

        return response

    def _set_final_decision(self, response, result, source):
        prob_ai = result.get("prob_ai", 0.0)
        prob_real = result.get("prob_real", 0.0)
        label = "ai_generated" if prob_ai >= 0.5 else "real"
        
        response["final_decision"] = {
            "label": label,
            "prob_ai": prob_ai,
            "prob_real": prob_real,
            "source": source
        }

# Singleton instance
detection_service = DetectionService()
