# =============================================
#   core/image_engine.py
#   Hugging Face Image Generation Engine
#   Model: FLUX.1-schnell (photorealistic)
# =============================================

import os
import requests
from dotenv import load_dotenv

load_dotenv()


class ImageEngine:
    """
    Handles image generation via Hugging Face Inference API.
    Uses FLUX.1-schnell for photorealistic marketing visuals.
    """

    def __init__(self):
        api_key = os.getenv("HF_API_KEY")
        if not api_key or api_key == "hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx":
            raise ValueError(
                "HF_API_KEY not set. Please add your key to the .env file."
            )
        self.api_key  = api_key
        self.model    = os.getenv("HF_MODEL", "black-forest-labs/FLUX.1-schnell")
        self.api_url  = f"https://router.huggingface.co/hf-inference/models/{self.model}"
        self.headers  = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type":  "application/json",
        }

    def generate_image(self, prompt: str) -> bytes:
        """
        Generate a photorealistic image from a text prompt.

        Args:
            prompt : Detailed image generation prompt

        Returns:
            bytes: Raw PNG image bytes ready for display
        """

        payload = {
            "inputs": prompt,
            "parameters": {
                "num_inference_steps": 4,   # FLUX.schnell is optimized for 4 steps
                "guidance_scale":      0.0, # FLUX.schnell uses 0 guidance scale
                "width":               1024,
                "height":              1024,
            }
        }

        response = requests.post(
            self.api_url,
            headers=self.headers,
            json=payload,
            timeout=120,
        )

        # Model warming up
        if response.status_code == 503:
            raise RuntimeError(
                "Model is loading on Hugging Face servers. "
                "Please wait 20-30 seconds and try again."
            )

        if response.status_code != 200:
            raise RuntimeError(
                f"Image generation failed: {response.status_code} — {response.text[:300]}"
            )

        return response.content  # raw PNG bytes

    def build_marketing_prompt(
        self,
        topic: str,
        audience: str,
        tone: str,
        platform: str,
        content_type: str,
        image_prompt: str = "",
    ) -> str:
        """
        Build an optimized photorealistic prompt for marketing content.

        Returns:
            str: Final prompt ready for FLUX.1-schnell
        """

        if image_prompt:
            base = image_prompt
        else:
            base = (
                f"Professional marketing photo for {topic}, "
                f"targeting {audience}, {tone} style, "
                f"suitable for {platform} {content_type}"
            )

        # FLUX responds well to photography-style descriptors
        quality_suffix = (
            ", photorealistic, professional product photography, "
            "commercial advertising photo, sharp focus, "
            "studio lighting, high resolution, 4K"
        )

        return base + quality_suffix