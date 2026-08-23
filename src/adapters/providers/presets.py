from __future__ import annotations

PROVIDER_PRESETS: dict[str, dict] = {
    "ollama": {
        "label": "Ollama (local)",
        "base_url": "http://localhost:11434/v1",
        "default_model": "llama3.2",
        "needs_key": False,
        "models": ["llama3.2", "llama3.1", "qwen2.5-coder", "deepseek-coder-v2", "mistral"],
    },
    "groq": {
        "label": "Groq",
        "base_url": "https://api.groq.com/openai/v1",
        "default_model": "llama-3.3-70b-versatile",
        "needs_key": True,
        "models": [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma2-9b-it",
        ],
    },
    "gemini": {
        "label": "Google Gemini",
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "default_model": "gemini-2.0-flash",
        "needs_key": True,
        "models": ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
    },
    "openai": {
        "label": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o-mini",
        "needs_key": True,
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4.1", "gpt-4.1-mini", "o4-mini"],
    },
    "opencode": {
        "label": "OpenCode Inference",
        "base_url": "https://opencode.ai/inference/openai/v1",
        "default_model": "big-pickle",
        "needs_key": True,
        "models": [
            "big-pickle",
            "deepseek-v4-flash",
            "deepseek-v4-pro",
            "glm-5",
            "glm-5.1",
            "kimi-k2.5",
            "kimi-k2.6",
            "kimi-k2.7-code",
            "minimax-m2.5",
            "hy3-free",
            "mimo-v2.5-free",
            "nemotron-3-ultra-free",
        ],
    },
    "zen": {
        "label": "OpenCode Zen",
        "base_url": "https://opencode.ai/zen/v1",
        "default_model": "glm-4.6",
        "needs_key": True,
        "models": [
            "glm-4.6",
            "glm-4.7-free",
            "kimi-k2",
            "kimi-k2-thinking",
            "big-pickle",
            "gpt-5",
            "gpt-5.1",
            "gpt-5.2",
            "claude-sonnet-4-5",
            "claude-haiku-4-5",
            "gemini-3-flash",
        ],
    },
    "openai_compatible": {
        "label": "Custom OpenAI-compatible",
        "base_url": "",
        "default_model": "",
        "needs_key": True,
        "models": [],
    },
}


def get_preset(provider: str) -> dict:
    return PROVIDER_PRESETS.get(provider, PROVIDER_PRESETS["openai_compatible"])
