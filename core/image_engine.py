# =============================================
#   core/image_engine.py
#   Hugging Face Image Generation Engine
# =============================================

import os
import io
import requests
from dotenv import load_dotenv

load_dotenv()


class ImageEngine:
    """
    Handles image generation via Hugging Face Inference API.
    Uses Stable Diffusion XL to generate marketing visuals.
    """

    def __init__(self):
        api_key = os.getenv("HF_API_KEY")
        if not api_key or api_key == "hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx":
            raise ValueError(
                "HF_API_KEY not set. Please add your key to the .env file."
            )
        self.api_key = api_key
        self.model   = os.getenv("HF_MODEL", "stabilityai/stable-diffusion-xl-base-1.0")
        self.api_url = f"https://router.huggingface.co/hf-inference/models/{self.model}"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def generate_image(self, prompt: str, negative_prompt: str = "") -> bytes:
        """
        Generate an image from a text prompt.

        Args:
            prompt          : Detailed image generation prompt
            negative_prompt : What to avoid in the image

        Returns:
            bytes: Raw PNG image bytes ready for display
        """

        payload = {
            "inputs": prompt,
            "parameters": {
                "negative_prompt": negative_prompt or "blurry, low quality, distorted, watermark, text, ugly",
                "num_inference_steps": 30,
                "guidance_scale": 7.5,
                "width": 1024,
                "height": 1024,
            }
        }

        response = requests.post(
            self.api_url,
            headers=self.headers,
            json=payload,
            timeout=120,  # image generation can take up to 60s
        )

        # Model loading — HF warms up cold models
        if response.status_code == 503:
            raise RuntimeError(
                "Model is loading on Hugging Face servers. "
                "Please wait 20-30 seconds and try again."
            )

        if response.status_code != 200:
            raise RuntimeError(
                f"Image generation failed: {response.status_code} — {response.text[:200]}"
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
        Build an optimized image generation prompt for marketing content.
        Uses the AI-generated image_prompt if available, otherwise builds one.

        Returns:
            str: Final prompt ready for Stable Diffusion
        """

        if image_prompt:
            # Use the Groq-generated image prompt as base
            base = image_prompt
        else:
            # Build a default marketing prompt
            base = (
                f"Professional marketing visual for {topic}, "
                f"targeting {audience}, {tone} style, "
                f"suitable for {platform} {content_type}"
            )

        # Append quality boosters for better output
        quality_suffix = (
            ", professional photography, high resolution, "
            "commercial quality, well-lit, sharp focus, "
            "marketing campaign visual, 4K"
        )

        return base + quality_suffix