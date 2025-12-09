import sys
import os
import torch
from PIL import Image
import yaml
import numpy as np
from torchvision.transforms import Compose, Resize, CenterCrop, InterpolationMode

# Add vendor directory to sys.path
# sys.path modification moved to __init__ to ensure correct timing and scope

from app.config import PRIMARY_WEIGHTS_DIR, PRIMARY_MODEL_NAME, DEVICE

class PrimaryModel:
    def __init__(self, weights_dir: str = PRIMARY_WEIGHTS_DIR, model_name: str = PRIMARY_MODEL_NAME, device: str = DEVICE):
        self.device = device
        self.weights_dir = weights_dir
        self.model_name = model_name
        
        # Setup path to vendored code
        vendor_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../vendor/clipbased"))
        if vendor_path not in sys.path:
            sys.path.insert(0, vendor_path)
            
        # Lazy import vendored modules
        try:
            from utils.processing import make_normalize
            from networks import create_architecture, load_weights
        except ImportError as e:
            raise ImportError(f"Failed to import vendored modules from {vendor_path}. Error: {e}. sys.path: {sys.path}. sys.modules['utils']: {sys.modules.get('utils')}")

        # Load config
        config_path = os.path.join(weights_dir, model_name, 'config.yaml')
        with open(config_path) as fid:
            self.config = yaml.load(fid, Loader=yaml.FullLoader)
        
        model_path = os.path.join(weights_dir, model_name, self.config['weights_file'])
        
        # Initialize model
        self.model = create_architecture(self.config['arch'])
        self.model = load_weights(self.model, model_path)
        self.model = self.model.to(self.device).eval()
        
        # Setup transform
        self.transform = self._build_transform(self.config, make_normalize)

    def _build_transform(self, config, make_normalize_fn):
        patch_size = config['patch_size']
        norm_type = config['norm_type']
        transform = []
        
        if patch_size == 'Clip224':
            transform.append(Resize(224, interpolation=InterpolationMode.BICUBIC))
            transform.append(CenterCrop((224, 224)))
        elif isinstance(patch_size, (tuple, list)):
            transform.append(Resize(*patch_size))
            transform.append(CenterCrop(patch_size[0]))
        elif patch_size > 0:
            transform.append(CenterCrop(patch_size))
            
        transform.append(make_normalize_fn(norm_type))
        return Compose(transform)

    def predict(self, image: Image.Image) -> dict:
        try:
            img_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                out_tens = self.model(img_tensor).cpu().numpy()
                
            if out_tens.shape[1] == 1:
                logit = out_tens[0, 0]
            elif out_tens.shape[1] == 2:
                logit = out_tens[0, 1] - out_tens[0, 0]
            else:
                raise ValueError("Unexpected output shape")

            # Convert logit to probability using sigmoid
            prob = 1 / (1 + np.exp(-logit))
            
            # Since the model detects "synthetic" images (AI), prob is prob_ai
            prob_ai = float(prob)
            prob_real = 1.0 - prob_ai
            
            # Confidence is the max logic, but scaled. 
            # If prob > 0.5, it's AI. Confidence is |prob - 0.5| * 2? 
            # Or just max(prob_ai, prob_real)
            confidence = max(prob_ai, prob_real)
            
            return {
                "prob_ai": prob_ai,
                "prob_real": prob_real,
                "confidence": confidence
            }
        except Exception as e:
            raise e
