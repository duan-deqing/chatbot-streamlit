"""模块常量

定义内置模型配置、Key 前缀、供应商显示名称等全局常量。
"""

import os
from config import OLLAMA_BASE_URL
from models.base import ModelConfig

CUSTOM_MODELS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "custom_models.json"
)

PREFIX_OPENAI = "openai_"
PREFIX_OLLAMA = "ollama_"
PREFIX_CUSTOM = "custom_"
KEY_OLLAMA_DEFAULT = "ollama_default"

OPENAI_MODELS = {
    "gpt-3.5-turbo": ModelConfig(
        name="GPT-3.5 Turbo",
        model_id="gpt-3.5-turbo",
        provider="openai",
        is_builtin=True,
        temperature=0.7,
        max_tokens=1000,
        top_p=0.9,
    ),
    "gpt-4": ModelConfig(
        name="GPT-4",
        model_id="gpt-4",
        provider="openai",
        is_builtin=True,
        temperature=0.7,
        max_tokens=1000,
        top_p=0.9,
    ),
    "gpt-4-turbo": ModelConfig(
        name="GPT-4 Turbo",
        model_id="gpt-4-turbo-preview",
        provider="openai",
        is_builtin=True,
        temperature=0.7,
        max_tokens=1000,
        top_p=0.9,
    ),
}

DEFAULT_OLLAMA_CONFIG = ModelConfig(
    name="Ollama 默认模型 (llama2)",
    model_id="llama2",
    provider="ollama",
    base_url=OLLAMA_BASE_URL,
    is_builtin=True,
    temperature=0.7,
    max_tokens=1000,
    top_p=0.9,
)

PROVIDER_DISPLAY = {
    "ollama": "本地 (Ollama)",
    "openai": "OpenAI",
}