import logging
from openai import AsyncOpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL, SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def get_gpt_response(prompt: str) -> str:
    """
    Get a response from the OpenAI GPT model.

    Args:
        prompt: The user prompt to send to the model

    Returns:
        The model's response text
    """
    try:
        response = await client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            model=OPENAI_MODEL,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error getting GPT response: {e}")
        raise