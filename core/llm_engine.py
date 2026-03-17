# =============================================
#   core/llm_engine.py
#   Groq API connection & content generation
# =============================================

import os
from groq import Groq
from dotenv import load_dotenv
from prompts.templates import CONTENT_TEMPLATES, TONE_DESCRIPTIONS

load_dotenv()


class LLMEngine:
    """Handles all communication with the Groq LLM API."""

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "your_groq_api_key_here":
            raise ValueError(
                "GROQ_API_KEY not set. Please add your key to the .env file."
            )
        self.client = Groq(api_key=api_key)
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.max_tokens = int(os.getenv("MAX_TOKENS", 1024))
        self.temperature = float(os.getenv("TEMPERATURE", 0.75))

    def generate_content(
        self,
        content_type: str,
        topic: str,
        audience: str,
        tone: str,
        platform: str,
        usp: str,
        similar_context: str = "",
    ) -> dict:
        """
        Generate marketing content using Groq.

        Args:
            content_type    : One of the 4 content types
            topic           : Product or campaign topic
            audience        : Target audience description
            tone            : Brand tone key
            platform        : Platform/channel
            usp             : Unique selling point or key message
            similar_context : Retrieved past content from VectorDB

        Returns:
            dict with content, model, tokens_used
        """

        if content_type not in CONTENT_TEMPLATES:
            raise ValueError(f"Unknown content type: {content_type}")

        template = CONTENT_TEMPLATES[content_type]

        # Build context section if similar content was found
        context_section = ""
        if similar_context:
            context_section = f"""
Previously Generated Similar Content (use for brand consistency reference):
---
{similar_context}
---
Maintain consistency in tone and style with the above, but create fresh new content."""

        # Get tone description
        tone_desc = TONE_DESCRIPTIONS.get(tone, tone)

        # Format the user prompt with all inputs
        user_prompt = template["user"].format(
            topic=topic,
            audience=audience,
            tone=f"{tone} ({tone_desc})",
            platform=platform,
            usp=usp,
            context_section=context_section,
        )

        # Call Groq API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": template["system"]},
                {"role": "user",   "content": user_prompt},
            ],
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )

        content     = response.choices[0].message.content
        tokens_used = response.usage.total_tokens

        return {
            "content":      content,
            "model":        self.model,
            "tokens_used":  tokens_used,
            "content_type": content_type,
            "topic":        topic,
            "tone":         tone,
            "platform":     platform,
        }

    def generate_image_prompt(
        self,
        content_type: str,
        topic: str,
        audience: str,
        tone: str,
        platform: str,
    ) -> str:
        """
        Generate an AI image prompt for the marketing content.

        Returns:
            str: A detailed image generation prompt
        """
        from prompts.templates import IMAGE_PROMPT_TEMPLATE

        prompt = IMAGE_PROMPT_TEMPLATE.format(
            content_type=content_type,
            topic=topic,
            audience=audience,
            tone=tone,
            platform=platform,
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.85,
        )

        return response.choices[0].message.content.strip()