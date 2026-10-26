"""LLM + embeddings via OpenAI SDK."""
from typing import List, Optional
from openai import OpenAI
from app.core.config import settings

_client: Optional[OpenAI] = None


def client() -> OpenAI:
    global _client
    if _client is None:
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY must be set to use AI features")
        _client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _client


def embed(text: str) -> List[float]:
    model = settings.EMBEDDING_MODEL
    resp = client().embeddings.create(model=model, input=text)
    return resp.data[0].embedding


def chat(system: str, user: str, temperature: float = 0.2) -> str:
    model = settings.LLM_MODEL
    resp = client().chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=temperature,
    )
    return resp.choices[0].message.content or ""


EMERGENCY_KEYWORDS = [
    "chest pain", "difficulty breathing", "suicidal", "severe bleeding", "unconscious",
]

def emergency_check(text: str) -> bool:
    low = text.lower()
    return any(k in low for k in EMERGENCY_KEYWORDS)


EMERGENCY_MESSAGE = (
    "This may be an emergency. Please seek immediate medical attention: call your local "
    "emergency number (e.g., 112/911) or go to the nearest emergency department. "
    "AI-generated, not medical advice."
)
