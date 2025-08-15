from __future__ import annotations
from typing import List, Dict, Any, Optional
import os
import requests

"""
LLM Provider abstraction with free-first strategy.
- Tries OpenRouter if OPENROUTER_API_KEY is present
- Otherwise returns a rule-based fallback response

Use: generate_text(system: str, messages: List[Dict[str,str]], model: Optional[str])
messages = [{"role":"user"|"assistant"|"system", "content":"..."}]
"""

OPENROUTER_API = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")


def _openrouter_generate(system: str, messages: List[Dict[str, str]], model: Optional[str] = None) -> str:
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        return ""
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model or DEFAULT_MODEL,
        "messages": ([{"role": "system", "content": system}] if system else []) + messages,
    }
    try:
        resp = requests.post(OPENROUTER_API, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return ""


def generate_text(system: str, messages: List[Dict[str, str]], model: Optional[str] = None) -> str:
    # Try OpenRouter first
    text = _openrouter_generate(system, messages, model)
    if text:
        return text
    # Fallback rule-based minimal response
    user_last = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
    return (
        "[Fallback AI] I understand your request. At the moment no free LLM key is configured. "
        "Please add an OPENROUTER_API_KEY or another provider to enable full AI replies. "
        f"Echo of your message: {user_last[:200]}"
    )

__all__ = ["generate_text"]