import os
from dotenv import load_dotenv
from groq import Groq
from langchain_groq import ChatGroq

load_dotenv()

MODEL = "openai/gpt-oss-120b"
DEFAULT_TEMPERATURE = 0.1
DEFAULT_MAX_TOKENS = 2048

_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def get_langchain_llm():
    return ChatGroq(
        model="openai/gpt-oss-120b",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.1,
    )

def chat(messages: list[dict], tools: list[dict] | None = None,
         temperature: float = DEFAULT_TEMPERATURE,
         max_tokens: int = DEFAULT_MAX_TOKENS):
    
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