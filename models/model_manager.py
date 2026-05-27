"""模型管理器

负责管理所有 AI 模型实例的生命周期，包括：
- 内置模型（OpenAI 系列、Ollama 本地默认模型）的初始化
- 自定义模型的持久化 CRUD（JSON 文件）
- 供应商（Provider）分组管理与自动检测
- API Key 的分层存储（供应商级与模型级）
"""

import json
import os
import uuid
from typing import Dict, List, Optional, Tuple
from config import OLLAMA_BASE_URL
from models.base import BaseModel, ModelConfig
from models.openai_model import OpenAIModel
from models.ollama_model import OllamaModel

# 自定义模型持久化文件路径
CUSTOM_MODELS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "custom_models.json")

# 内置 OpenAI 模型定义
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

# Ollama 默认配置（作为连接检测 & 占位模型，有本地模型时自动隐藏）
DEFAULT_OLLAMA_CONFIG = ModelConfig(
    name="Ollama 默认模型 (llama2)",
    model_id="llama2",
    provider="ollama",
    base_url=OLLAMA_BASE_URL,
    is_builtin=True,
    temperature=0.7,
    max_tokens=1000,
    top_p=0.9
)


class ModelManager:
    """模型管理器

    核心职责：
    1. 维护所有模型实例的注册表 (_models)
    2. 管理自定义模型配置的持久化 (_custom_configs → JSON)
    3. 管理供应商级 API Key (_provider_api_keys)
    4. 按供应商分组暴露模型列表（供 UI 双级联动 selectbox 使用）
    """

    # 供应商显示名称映射
    PROVIDER_DISPLAY = {
        "ollama": "本地 (Ollama)",
        "openai": "OpenAI",
    }

    def __init__(self):
        self._models: Dict[str, BaseModel] = {}             # 模型实例注册表，key 为如 "openai_gpt-4" 或 "custom_a1b2c3d4"
        self._custom_configs: Dict[str, ModelConfig] = {}    # 自定义模型配置，key 为如 "custom_a1b2c3d4"
        self._provider_api_keys: Dict[str, str] = {}         # 供应商级 API Key，如 {"openai": "sk-..."}
        self._load_custom_configs()                          # 从 JSON 恢复持久化数据
        self._init_models()                                  # 创建所有模型实例

    def _init_models(self):
        """初始化所有模型实例

        1. 注册内置 OpenAI 模型（key 格式: openai_{model_name}）
        2. 注册 Ollama 默认占位模型（key 格式: ollama_default）
        3. 根据持久化配置注册自定义模型（key 格式: custom_{uuid}）
        """
        for model_key, config in OPENAI_MODELS.items():
            key = f"openai_{model_key}"
            self._models[key] = OpenAIModel(config)

        self._models["ollama_default"] = OllamaModel(DEFAULT_OLLAMA_CONFIG)

        for custom_key, config in self._custom_configs.items():
            self._models[custom_key] = OpenAIModel(config)

    def get_model(self, model_key: str) -> Optional[BaseModel]:
        """按 key 获取模型实例（不含 API Key 注入）"""
        return self._models.get(model_key)

    def get_all_models(self) -> Dict[str, BaseModel]:
        """获取所有模型实例"""
        return self._models

    def get_current_model(self, model_key: str) -> Optional[BaseModel]:
        """获取当前模型实例并注入 API Key

        自动尝试两处 API Key：
        1. 模型自身配置的 api_key（自定义模型配置中存储）
        2. 供应商级的 api_key（仅对 OpenAI 生效）

        这样 chat.py 调用时无需关心 Key 来源。
        """
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

        供应商排序规则：
        1. Ollama 始终第一位
        2. 自定义供应商按添加顺序排在中间
        3. OpenAI 始终最后一位

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

        Ollama 特有行为：自动检测本地已安装模型并注册到列表中，
        实现了「选择供应商即自动加载模型」的体验。

        Args:
            provider_key: 供应商标识

        Returns:
            [(model_key, display_name), ...]，自定义模型带 ⚙️ 前缀
        """
        models = []

        if provider_key == "ollama":
            # 自动检测本地 Ollama 模型
            ollama_default = self.get_ollama_default()
            has_local_models = False
            if ollama_default and ollama_default.get_cached_status():
                local_models = ollama_default.list_models()
                for model_id in local_models:
                    key = f"ollama_{model_id}"
                    if key not in self._models:
                        self.add_ollama_model(model_id)
                has_local_models = bool(local_models)
            # 遍历所有 ollama_ 开头的模型
            for key, model in self._models.items():
                if key.startswith("ollama_"):
                    # 有真实本地模型时隐藏占位模型，避免重复
                    if key == "ollama_default" and has_local_models:
                        continue
                    models.append((key, model.name))

        elif provider_key == "openai":
            for key, model in self._models.items():
                if key.startswith("openai_"):
                    models.append((key, model.name))

        else:
            # 自定义供应商，仅返回属于该供应商的自定义模型
            for key, model in self._models.items():
                if key.startswith("custom_") and model.config.provider == provider_key:
                    models.append((key, "⚙️ " + model.name))

        return models

    def add_ollama_model(self, model_id: str, name: str = None) -> str:
        """手动注册一个 Ollama 模型（不在 JSON 持久化范围内）

        Ollama 模型通过自动检测机制载入，不需要持久化存储。
        """
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
        """获取 Ollama 默认模型实例（用于连接检测）"""
        return self._models.get("ollama_default")

    def get_openai_models(self) -> Dict[str, OpenAIModel]:
        """获取所有 OpenAI 模型实例"""
        return {k: v for k, v in self._models.items() if isinstance(v, OpenAIModel)}

    def get_ollama_models(self) -> Dict[str, OllamaModel]:
        """获取所有 Ollama 模型实例"""
        return {k: v for k, v in self._models.items() if isinstance(v, OllamaModel)}

    def set_openai_api_key(self, api_key: str):
        """设置 OpenAI 供应商的 API Key 并同步到所有 OpenAI 模型实例

        同时持久化到 JSON 文件。
        """
        self._provider_api_keys["openai"] = api_key
        for model in self.get_openai_models().values():
            model.set_api_key(api_key)
        self._save_custom_configs()

    def get_provider_api_key(self, provider_key: str) -> str:
        """获取指定供应商的 API Key"""
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
        """添加自定义模型配置（持久化 + 立即生效）

        Args:
            name: 显示名称
            model_id: API 调用的模型标识
            provider: 供应商标识（会出现在供应商下拉列表中）
            base_url: API 端点地址
            api_key: API Key（可选，与模型配置关联存储）
            temperature: 温度参数（创造性）
            max_tokens: 最大输出 token 数
            top_p: 核采样

        Returns:
            新创建模型的 key（格式: custom_{8位uuid}）
        """
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
        """编辑已有自定义模型配置（直接原地更新，不改变 key）"""
        if key not in self._custom_configs:
            return False
        config = self._custom_configs[key]
        config.name = name
        config.model_id = model_id
        config.provider = provider
        config.base_url = base_url
        config.api_key = api_key
        # 重建模型实例以应用新配置
        self._models[key] = OpenAIModel(config)
        self._save_custom_configs()
        return True

    def delete_custom_model(self, key: str) -> bool:
        """删除自定义模型（同时从内存和持久化中移除）"""
        if key not in self._custom_configs:
            return False
        del self._custom_configs[key]
        self._models.pop(key, None)
        self._save_custom_configs()
        return True

    def get_custom_models(self) -> Dict[str, ModelConfig]:
        """获取所有自定义模型配置"""
        return self._custom_configs

    def is_custom_model(self, key: str) -> bool:
        """判断指定 key 是否为自定义模型"""
        return key in self._custom_configs

    def _save_custom_configs(self):
        """将自定义模型配置和供应商 API Key 持久化到 JSON 文件

        存储结构：
        {
            "custom_models": { "custom_xxx": { "name": "...", ... } },
            "provider_api_keys": { "openai": "sk-..." }
        }
        """
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
        """从 JSON 文件恢复自定义模型配置和供应商 API Key

        失败时优雅降级为空字典，不阻塞应用启动。
        """
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