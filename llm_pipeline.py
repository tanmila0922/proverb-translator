"""
OpenRouter API wrapper for Chinese proverb analysis.
Checks local dataset first; falls back to LLM for unknown proverbs.
"""

import json
import os
import random
from difflib import SequenceMatcher

import requests
import streamlit as st

SYSTEM_PROMPT = (
    "You are a Chinese-Russian cultural linguistics expert. "
    "Analyze the given Chinese proverb and return a JSON object with these exact keys: "
    "literal, meaning, russian_equivalent, what_gets_lost, tone, cultural_context, category, difficulty. "
    "Be scholarly but accessible. The Russian equivalent should be a real Russian proverb or saying, "
    "not a literal translation. 'what_gets_lost' should analyze specific semantic/cultural gaps "
    "between the Chinese and Russian versions. "
    "category must be one of: wisdom, family, perseverance, nature, social_conduct, warning, humor, love. "
    "difficulty must be one of: beginner, intermediate, advanced. "
    "Return ONLY valid JSON, no markdown fences or extra text."
)

DEFAULT_MODEL = "moonshotai/kimi-k2.5"

COMPARE_MODELS = [
    "moonshotai/kimi-k2.5",
    "deepseek/deepseek-chat-v3-0324:free",
    "meta-llama/llama-4-maverick:free",
]


def _get_api_key() -> str:
    try:
        return st.secrets["OPENROUTER_API_KEY"]
    except Exception:
        return os.environ.get("OPENROUTER_API_KEY", "")


def _build_few_shot(examples: list[dict]) -> list[dict]:
    shots = random.sample(examples, min(3, len(examples)))
    messages = []
    for s in shots:
        messages.append({"role": "user", "content": f"Analyze: {s['chinese']}"})
        answer = json.dumps(
            {
                "literal": s["literal"],
                "meaning": s["meaning"],
                "russian_equivalent": s["russian_equivalent"],
                "what_gets_lost": s["what_gets_lost"],
                "tone": s.get("tone", ""),
                "cultural_context": s.get("cultural_context", ""),
                "category": s.get("category", "wisdom"),
                "difficulty": s.get("difficulty", "intermediate"),
            },
            ensure_ascii=False,
        )
        messages.append({"role": "assistant", "content": answer})
    return messages


def fuzzy_match(query: str, dataset: list[dict], threshold: float = 0.7) -> dict | None:
    query = query.strip()
    for entry in dataset:
        if query == entry["chinese"] or query == entry.get("pinyin", ""):
            return entry
        ratio = SequenceMatcher(None, query, entry["chinese"]).ratio()
        if ratio >= threshold:
            return entry
    return None


def call_openrouter(
    chinese_text: str,
    examples: list[dict],
    model: str = DEFAULT_MODEL,
) -> dict:
    api_key = _get_api_key()
    if not api_key:
        return {"error": "No API key configured. Set OPENROUTER_API_KEY in Streamlit secrets or environment."}

    few_shot = _build_few_shot(examples)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *few_shot,
        {"role": "user", "content": f"Analyze: {chinese_text}"},
    ]

    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={"model": model, "messages": messages, "temperature": 0.3},
            timeout=60,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        content = content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1] if "\n" in content else content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
        return json.loads(content)
    except requests.exceptions.Timeout:
        return {"error": f"Request to {model} timed out. Try again."}
    except requests.exceptions.HTTPError as e:
        return {"error": f"API error ({e.response.status_code}): {e.response.text[:200]}"}
    except (json.JSONDecodeError, KeyError, IndexError):
        return {"error": "Model returned invalid JSON. Try a different proverb or model."}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)[:200]}"}


def analyze(chinese_text: str, dataset: list[dict], model: str = DEFAULT_MODEL) -> tuple[dict, str]:
    """
    Returns (result_dict, source_label).
    source_label is either "Human-annotated" or "AI-generated ({model})".
    """
    match = fuzzy_match(chinese_text, dataset)
    if match:
        return match, "Human-annotated"

    result = call_openrouter(chinese_text, dataset, model=model)
    return result, f"AI-generated ({model})"
