import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# ----- Configuration -----
MODEL = "openai/gpt-oss-120b"
DEFAULT_TEMPERATURE = 0.1
DEFAULT_MAX_TOKENS = 2048

# Client singleton (créé une seule fois)
_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def chat(messages: list[dict], tools: list[dict] | None = None,
         temperature: float = DEFAULT_TEMPERATURE,
         max_tokens: int = DEFAULT_MAX_TOKENS):
    """
    Envoie une conversation au LLM et retourne la réponse brute.

    Args:
        messages: liste de {"role": ..., "content": ...}
        tools:    liste de définitions d'outils (format OpenAI-compatible)
        temperature: 0 = déterministe, 1 = créatif
        max_tokens: longueur max de la réponse

    Returns:
        L'objet message de l'assistant (response.choices[0].message)
    """
    kwargs = {
        "model": MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"

    response = _client.chat.completions.create(**kwargs)
    return response.choices[0].message