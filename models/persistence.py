"""模型配置持久化

负责自定义模型配置和供应商 API Key 的 JSON 文件存取。
"""

import json
import os
from typing import Dict, Tuple
from models.base import ModelConfig


class ModelPersistence:
    """自定义模型配置的 JSON 持久化

    封装所有与 JSON 文件交互的逻辑：
    - 加载：从文件反序列化为 ModelConfig 字典
    - 保存：将内存配置序列化写入文件
    - 同时管理 provider_api_keys 的持久化
    """

    def __init__(self, file_path: str):
        self._file_path = file_path

    def load(self) -> Tuple[Dict[str, ModelConfig], Dict[str, str]]:
        """从 JSON 文件加载自定义模型配置和供应商 API Key

        Returns:
            (custom_configs, provider_api_keys)
        """
        try:
            if not os.path.exists(self._file_path):
                return {}, {}
            with open(self._file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            provider_api_keys = data.get("provider_api_keys", {})
            custom_configs = {}
            for key, cfg in data.get("custom_models", {}).items():
                custom_configs[key] = self._dict_to_config(cfg)
            return custom_configs, provider_api_keys
        except Exception:
            return {}, {}

    def save(
        self,
        custom_configs: Dict[str, ModelConfig],
        provider_api_keys: Dict[str, str],
    ):
        """将自定义模型配置和供应商 API Key 持久化到 JSON 文件"""
        data = {
            "custom_models": {
                key: self._config_to_dict(config)
                for key, config in custom_configs.items()
            },
            "provider_api_keys": provider_api_keys,
        }
        try:
            os.makedirs(os.path.dirname(self._file_path), exist_ok=True)
            with open(self._file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    @staticmethod
    def _config_to_dict(config: ModelConfig) -> dict:
        return {
            "name": config.name,
            "model_id": config.model_id,
            "provider": config.provider,
            "base_url": config.base_url,
            "api_key": config.api_key,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "top_p": config.top_p,
        }

    @staticmethod
    def _dict_to_config(cfg: dict) -> ModelConfig:
        return ModelConfig(
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