"""模型管理器

负责管理所有 AI 模型实例的生命周期，包括：
- 内置模型（OpenAI 系列、Ollama 本地默认模型）的初始化
- 自定义模型的持久化 CRUD（JSON 文件）
- 供应商（Provider）分组管理与自动检测
- API Key 的分层存储（供应商级与模型级）
"""

import uuid
from typing import Dict, List, Optional, Tuple

from config import OLLAMA_BASE_URL
from models.base import BaseModel, ModelConfig
from models.openai_model import OpenAIModel
from models.ollama_model import OllamaModel
from models.constants import (
    CUSTOM_MODELS_FILE,
    PREFIX_OPENAI,
    PREFIX_OLLAMA,
    PREFIX_CUSTOM,
    KEY_OLLAMA_DEFAULT,
    OPENAI_MODELS,
    DEFAULT_OLLAMA_CONFIG,
    PROVIDER_DISPLAY,
)
from models.persistence import ModelPersistence


class ModelManager:
    """模型管理器

    核心职责：
    1. 维护所有模型实例的注册表 (_models)
    2. 管理自定义模型配置的持久化 (_custom_configs → JSON)
    3. 管理供应商级 API Key (_provider_api_keys)
    4. 按供应商分组暴露模型列表（供 UI 双级联动 selectbox 使用）
    """

    def __init__(self):
        self._persistence = ModelPersistence(CUSTOM_MODELS_FILE)
        self._models: Dict[str, BaseModel] = {}
        self._custom_configs: Dict[str, ModelConfig] = {}
        self._provider_api_keys: Dict[str, str] = {}
        self._load_and_init()

    # ---- 初始化 ----

    def _load_and_init(self):
        self._custom_configs, self._provider_api_keys = self._persistence.load()
        self._init_builtin_models()
        self._init_custom_models()

    def _init_builtin_models(self):
        for model_key, config in OPENAI_MODELS.items():
            self._models[f"{PREFIX_OPENAI}{model_key}"] = OpenAIModel(config)
        self._models[KEY_OLLAMA_DEFAULT] = OllamaModel(DEFAULT_OLLAMA_CONFIG)

    def _init_custom_models(self):
        for custom_key, config in self._custom_configs.items():
            self._models[custom_key] = OpenAIModel(config)

    # ---- 模型获取 ----

    def get_model(self, model_key: str) -> Optional[BaseModel]:
        return self._models.get(model_key)

    def get_all_models(self) -> Dict[str, BaseModel]:
        return self._models

    def get_current_model(self, model_key: str) -> Optional[BaseModel]:
        """获取当前模型实例并注入 API Key

        自动尝试两处 API Key：
        1. 模型自身配置的 api_key（自定义模型配置中存储）
        2. 供应商级的 api_key（仅对 OpenAI 生效）
        """
        model = self._models.get(model_key)
        if model is None:
            return None
        if model.config.api_key:
            model.set_api_key(model.config.api_key)
        if model.config.provider == "openai":
            provider_key = self._provider_api_keys.get("openai", "")
            if provider_key:
                model.set_api_key(provider_key)
        return model

    # ---- 供应商 ----

    def get_providers(self) -> List[Tuple[str, str]]:
        """获取所有供应商列表（Ollama → 自定义 → OpenAI）"""
        providers = [("ollama", PROVIDER_DISPLAY.get("ollama", "本地 (Ollama)"))]

        for config in self._custom_configs.values():
            p_name = config.provider
            existing = {p[0] for p in providers}
            if p_name not in PROVIDER_DISPLAY and p_name not in existing:
                providers.append((p_name, p_name))

        providers.append(("openai", PROVIDER_DISPLAY.get("openai", "OpenAI")))
        return providers

    # ---- 按供应商获取模型 ----

    def get_models_by_provider(self, provider_key: str) -> List[Tuple[str, str]]:
        """获取指定供应商下的模型列表

        Ollama 特有行为：自动检测本地已安装模型并注册到列表中。
        自定义模型带 ⚙️ 前缀。
        """
        if provider_key == "ollama":
            return self._list_ollama_models()
        elif provider_key == "openai":
            return self._list_openai_models()
        else:
            return self._list_custom_provider_models(provider_key)

    def _list_ollama_models(self) -> List[Tuple[str, str]]:
        models = []
        ollama_default = self.get_ollama_default()
        has_local_models = False

        if ollama_default and ollama_default.get_cached_status():
            local_models = ollama_default.list_models()
            for model_id in local_models:
                key = f"{PREFIX_OLLAMA}{model_id}"
                if key not in self._models:
                    self.add_ollama_model(model_id)
            has_local_models = bool(local_models)

        for key, model in self._models.items():
            if not key.startswith(PREFIX_OLLAMA):
                continue
            if key == KEY_OLLAMA_DEFAULT and has_local_models:
                continue
            models.append((key, model.name))

        return models

    def _list_openai_models(self) -> List[Tuple[str, str]]:
        return [
            (key, model.name)
            for key, model in self._models.items()
            if key.startswith(PREFIX_OPENAI)
        ]

    def _list_custom_provider_models(self, provider_key: str) -> List[Tuple[str, str]]:
        return [
            (key, f"⚙️ {model.name}")
            for key, model in self._models.items()
            if key.startswith(PREFIX_CUSTOM) and model.config.provider == provider_key
        ]

    # ---- Ollama 管理 ----

    def add_ollama_model(self, model_id: str, name: str = None) -> str:
        config = ModelConfig(
            name=name or model_id,
            model_id=model_id,
            provider="ollama",
            base_url=OLLAMA_BASE_URL,
            is_builtin=False,
            temperature=0.7,
            max_tokens=1000,
            top_p=0.9,
        )
        key = f"{PREFIX_OLLAMA}{model_id}"
        self._models[key] = OllamaModel(config)
        return key

    def get_ollama_default(self) -> Optional[OllamaModel]:
        return self._models.get(KEY_OLLAMA_DEFAULT)

    def get_ollama_models(self) -> Dict[str, OllamaModel]:
        return {
            k: v for k, v in self._models.items() if isinstance(v, OllamaModel)
        }

    # ---- OpenAI 管理 ----

    def get_openai_models(self) -> Dict[str, OpenAIModel]:
        return {
            k: v for k, v in self._models.items() if isinstance(v, OpenAIModel)
        }

    def set_openai_api_key(self, api_key: str):
        self._provider_api_keys["openai"] = api_key
        for model in self.get_openai_models().values():
            model.set_api_key(api_key)
        self._persistence.save(self._custom_configs, self._provider_api_keys)

    def get_provider_api_key(self, provider_key: str) -> str:
        return self._provider_api_keys.get(provider_key, "")

    # ---- 自定义模型 CRUD ----

    def add_custom_model(
        self,
        name: str,
        model_id: str,
        provider: str,
        base_url: str,
        api_key: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        top_p: float = 0.9,
    ) -> str:
        key = f"{PREFIX_CUSTOM}{uuid.uuid4().hex[:8]}"
        config = ModelConfig(
            name=name,
            model_id=model_id,
            provider=provider,
            base_url=base_url,
            api_key=api_key,
            is_builtin=False,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
        )
        self._custom_configs[key] = config
        self._models[key] = OpenAIModel(config)
        self._persistence.save(self._custom_configs, self._provider_api_keys)
        return key

    def edit_custom_model(
        self,
        key: str,
        name: str,
        model_id: str,
        provider: str,
        base_url: str,
        api_key: str = "",
    ) -> bool:
        if key not in self._custom_configs:
            return False
        config = self._custom_configs[key]
        config.name = name
        config.model_id = model_id
        config.provider = provider
        config.base_url = base_url
        config.api_key = api_key
        self._models[key] = OpenAIModel(config)
        self._persistence.save(self._custom_configs, self._provider_api_keys)
        return True

    def delete_custom_model(self, key: str) -> bool:
        if key not in self._custom_configs:
            return False
        del self._custom_configs[key]
        self._models.pop(key, None)
        self._persistence.save(self._custom_configs, self._provider_api_keys)
        return True

    def get_custom_models(self) -> Dict[str, ModelConfig]:
        return self._custom_configs

    def is_custom_model(self, key: str) -> bool:
        return key in self._custom_configs