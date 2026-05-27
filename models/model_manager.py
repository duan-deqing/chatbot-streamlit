"""模型管理器"""

import json
import os
import uuid
from typing import Dict, List, Optional, Tuple
from config import OLLAMA_BASE_URL
from models.base import BaseModel, ModelConfig
from models.openai_model import OpenAIModel
from models.ollama_model import OllamaModel

CUSTOM_MODELS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "custom_models.json")

OPENAI_MODELS = {
    "gpt-3.5-turbo": ModelConfig(
        name="GPT-3.5 Turbo",
        model_id="gpt-3.5-turbo",
        provider="openai",
        is_builtin=True,
        temperature=0.7,
        max_tokens=1000,
        top_p=0.9
    ),
    "gpt-4": ModelConfig(
        name="GPT-4",
        model_id="gpt-4",
        provider="openai",
        is_builtin=True,
        temperature=0.7,
        max_tokens=1000,
        top_p=0.9
    ),
    "gpt-4-turbo": ModelConfig(
        name="GPT-4 Turbo",
        model_id="gpt-4-turbo-preview",
        provider="openai",
        is_builtin=True,
        temperature=0.7,
        max_tokens=1000,
        top_p=0.9
    )
}

DEFAULT_OLLAMA_CONFIG = ModelConfig(
    name="Ollama 本地模型",
    model_id="llama2",
    provider="ollama",
    base_url=OLLAMA_BASE_URL,
    is_builtin=True,
    temperature=0.7,
    max_tokens=1000,
    top_p=0.9
)


class ModelManager:
    """模型管理器"""

    PROVIDER_DISPLAY = {
        "ollama": "本地 (Ollama)",
        "openai": "OpenAI",
    }

    def __init__(self):
        self._models: Dict[str, BaseModel] = {}
        self._custom_configs: Dict[str, ModelConfig] = {}
        self._provider_api_keys: Dict[str, str] = {}
        self._load_custom_configs()
        self._init_models()

    def _init_models(self):
        for model_key, config in OPENAI_MODELS.items():
            key = f"openai_{model_key}"
            self._models[key] = OpenAIModel(config)

        self._models["ollama_default"] = OllamaModel(DEFAULT_OLLAMA_CONFIG)

        for custom_key, config in self._custom_configs.items():
            self._models[custom_key] = OpenAIModel(config)

    def get_model(self, model_key: str) -> Optional[BaseModel]:
        return self._models.get(model_key)

    def get_all_models(self) -> Dict[str, BaseModel]:
        return self._models

    def get_current_model(self, model_key: str) -> Optional[BaseModel]:
        model = self._models.get(model_key)
        if model and model.config.api_key:
            model.set_api_key(model.config.api_key)
        if model and model.config.provider == "openai":
            provider_key = self._provider_api_keys.get("openai", "")
            if provider_key:
                model.set_api_key(provider_key)
        return model

    def get_providers(self) -> List[Tuple[str, str]]:
        """获取所有供应商列表（本地模型固定第一位）
        
        Returns:
            [(provider_key, display_name), ...]
        """
        providers = []

        providers.append(("ollama", self.PROVIDER_DISPLAY.get("ollama", "本地 (Ollama)")))

        for custom_key, config in self._custom_configs.items():
            provider_name = config.provider
            if provider_name not in self.PROVIDER_DISPLAY and provider_name not in [p[0] for p in providers]:
                providers.append((provider_name, provider_name))

        providers.append(("openai", self.PROVIDER_DISPLAY.get("openai", "OpenAI")))

        return providers

    def get_models_by_provider(self, provider_key: str) -> List[Tuple[str, str]]:
        """获取指定供应商下的模型列表
        
        Args:
            provider_key: 供应商标识
            
        Returns:
            [(model_key, display_name), ...]，自定义模型带 ⚙️ 前缀
        """
        models = []

        if provider_key == "ollama":
            ollama_default = self.get_ollama_default()
            has_local_models = False
            if ollama_default and ollama_default.get_cached_status():
                local_models = ollama_default.list_models()
                for model_id in local_models:
                    key = f"ollama_{model_id}"
                    if key not in self._models:
                        self.add_ollama_model(model_id)
                has_local_models = bool(local_models)
            for key, model in self._models.items():
                if key.startswith("ollama_"):
                    if key == "ollama_default" and has_local_models:
                        continue
                    models.append((key, model.name))

        elif provider_key == "openai":
            for key, model in self._models.items():
                if key.startswith("openai_"):
                    models.append((key, model.name))

        else:
            for key, model in self._models.items():
                if key.startswith("custom_") and model.config.provider == provider_key:
                    models.append((key, "⚙️ " + model.name))

        return models

    def add_ollama_model(self, model_id: str, name: str = None) -> str:
        config = ModelConfig(
            name=name or model_id,
            model_id=model_id,
            provider="ollama",
            base_url=OLLAMA_BASE_URL,
            is_builtin=False,
            temperature=0.7,
            max_tokens=1000,
            top_p=0.9
        )
        key = f"ollama_{model_id}"
        self._models[key] = OllamaModel(config)
        return key

    def get_ollama_default(self) -> Optional[OllamaModel]:
        return self._models.get("ollama_default")

    def get_openai_models(self) -> Dict[str, OpenAIModel]:
        return {k: v for k, v in self._models.items() if isinstance(v, OpenAIModel)}

    def get_ollama_models(self) -> Dict[str, OllamaModel]:
        return {k: v for k, v in self._models.items() if isinstance(v, OllamaModel)}

    def set_openai_api_key(self, api_key: str):
        """设置 OpenAI 供应商的 API Key"""
        self._provider_api_keys["openai"] = api_key
        for model in self.get_openai_models().values():
            model.set_api_key(api_key)
        self._save_custom_configs()

    def get_provider_api_key(self, provider_key: str) -> str:
        return self._provider_api_keys.get(provider_key, "")

    def add_custom_model(
        self,
        name: str,
        model_id: str,
        provider: str,
        base_url: str,
        api_key: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        top_p: float = 0.9
    ) -> str:
        key = f"custom_{uuid.uuid4().hex[:8]}"
        config = ModelConfig(
            name=name,
            model_id=model_id,
            provider=provider,
            base_url=base_url,
            api_key=api_key,
            is_builtin=False,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p
        )
        self._custom_configs[key] = config
        self._models[key] = OpenAIModel(config)
        self._save_custom_configs()
        return key

    def edit_custom_model(self, key: str, name: str, model_id: str, provider: str,
                          base_url: str, api_key: str = "") -> bool:
        if key not in self._custom_configs:
            return False
        config = self._custom_configs[key]
        config.name = name
        config.model_id = model_id
        config.provider = provider
        config.base_url = base_url
        config.api_key = api_key
        self._models[key] = OpenAIModel(config)
        self._save_custom_configs()
        return True

    def delete_custom_model(self, key: str) -> bool:
        if key not in self._custom_configs:
            return False
        del self._custom_configs[key]
        self._models.pop(key, None)
        self._save_custom_configs()
        return True

    def get_custom_models(self) -> Dict[str, ModelConfig]:
        return self._custom_configs

    def is_custom_model(self, key: str) -> bool:
        return key in self._custom_configs

    def _save_custom_configs(self):
        data = {
            "custom_models": {},
            "provider_api_keys": self._provider_api_keys,
        }
        for key, config in self._custom_configs.items():
            data["custom_models"][key] = {
                "name": config.name,
                "model_id": config.model_id,
                "provider": config.provider,
                "base_url": config.base_url,
                "api_key": config.api_key,
                "temperature": config.temperature,
                "max_tokens": config.max_tokens,
                "top_p": config.top_p,
            }
        try:
            os.makedirs(os.path.dirname(CUSTOM_MODELS_FILE), exist_ok=True)
            with open(CUSTOM_MODELS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _load_custom_configs(self):
        try:
            if not os.path.exists(CUSTOM_MODELS_FILE):
                return
            with open(CUSTOM_MODELS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._provider_api_keys = data.get("provider_api_keys", {})
            for key, cfg in data.get("custom_models", {}).items():
                self._custom_configs[key] = ModelConfig(
                    name=cfg.get("name", ""),
                    model_id=cfg.get("model_id", ""),
                    provider=cfg.get("provider", ""),
                    base_url=cfg.get("base_url", ""),
                    api_key=cfg.get("api_key", ""),
                    is_builtin=False,
                    temperature=cfg.get("temperature", 0.7),
                    max_tokens=cfg.get("max_tokens", 1000),
                    top_p=cfg.get("top_p", 0.9),
                )
        except Exception:
            self._custom_configs = {}
            self._provider_api_keys = {}