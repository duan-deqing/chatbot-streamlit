"""Ollama 本地模型实现

通过 OpenAI 兼容协议与本地 Ollama 服务通信，使用 OpenAI Python SDK。
实现了带 TTL 的缓存机制以减少对 Ollama 服务的频繁探测。
"""

import time
import httpx
import openai
from typing import List, Dict, Optional, Generator
from models.base import BaseModel, ModelConfig


class OllamaModel(BaseModel):
    """Ollama 本地模型

    通过 Ollama 的 OpenAI 兼容端点（/v1）进行通信。

    缓存机制：
    - 服务状态和模型列表缓存在类级别变量中，所有实例共享
    - 默认 TTL 300 秒（5 分钟），避免每次 UI 交互都探测服务
    - refresh_cache() 强制使缓存失效，用于手动刷新
    """

    # 类级别缓存，所有实例共享
    _service_status_cache: Optional[bool] = None   # 服务是否可用
    _models_cache: Optional[List[str]] = None      # 已安装模型列表
    _last_check_time: float = 0                    # 上次探测时间戳
    _cache_ttl: float = 300                        # 缓存有效期 5 分钟

    def __init__(self, config: ModelConfig, base_url: str = ""):
        super().__init__(config)
        # base_url 优先级：显式传入 > config 配置 > Ollama 默认地址
        self.base_url = (base_url or config.base_url or "http://localhost:11434/v1").rstrip('/')
        # Ollama 不需要真实 API Key，传入任意占位值即可
        self.client = openai.OpenAI(
            base_url=self.base_url,
            api_key="ollama"
        )

    def chat(self, messages: List[Dict], **kwargs) -> str:
        """同步聊天

        Args:
            messages: OpenAI 格式消息列表
            **kwargs: temperature, max_tokens, top_p 可覆盖默认值

        Returns:
            模型回复，连接失败或调用出错时返回中文错误提示
        """
        try:
            temperature = kwargs.get("temperature", self.config.temperature)
            max_tokens = kwargs.get("max_tokens", self.config.max_tokens)
            top_p = kwargs.get("top_p", self.config.top_p)
            response = self.client.chat.completions.create(
                model=self.config.model_id,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p
            )
            return response.choices[0].message.content
        except (httpx.ConnectError, httpx.ConnectTimeout):
            return "❌ 无法连接到 Ollama 服务，请确保 Ollama 已启动。"
        except Exception as e:
            return f"⚠️ Ollama 调用出错: {str(e)}"

    def chat_stream(self, messages: List[Dict], **kwargs) -> Generator[str, None, None]:
        """流式聊天（SSE 逐 token 输出）

        Args:
            messages: OpenAI 格式消息列表
            **kwargs: temperature, max_tokens, top_p 可覆盖默认值

        Yields:
            逐段模型回复文本
        """
        try:
            temperature = kwargs.get("temperature", self.config.temperature)
            max_tokens = kwargs.get("max_tokens", self.config.max_tokens)
            top_p = kwargs.get("top_p", self.config.top_p)
            stream = self.client.chat.completions.create(
                model=self.config.model_id,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                stream=True
            )
            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield delta.content
        except (httpx.ConnectError, httpx.ConnectTimeout):
            yield "❌ 无法连接到 Ollama 服务，请确保 Ollama 已启动。"
        except Exception as e:
            yield f"⚠️ Ollama 调用出错: {str(e)}"

    def _is_cache_valid(self) -> bool:
        """缓存是否在有效期内"""
        return (time.time() - OllamaModel._last_check_time) < OllamaModel._cache_ttl

    def _update_cache(self, status: bool, models: List[str]):
        """更新类级别缓存"""
        OllamaModel._service_status_cache = status
        OllamaModel._models_cache = models
        OllamaModel._last_check_time = time.time()

    def is_available(self) -> bool:
        """检查 Ollama 服务是否可连接（带 5 分钟缓存）

        Returns:
            服务是否可用
        """
        if self._is_cache_valid() and OllamaModel._service_status_cache is not None:
            return OllamaModel._service_status_cache

        try:
            models = self.client.models.list()
            status = True
            model_list = [m.id for m in models.data]
            self._update_cache(status, model_list)
            return status
        except Exception:
            self._update_cache(False, [])
            return False

    def list_models(self) -> List[str]:
        """获取本地已安装模型列表（带 5 分钟缓存）

        Returns:
            模型 ID 列表，如 ["llama2", "qwen2:7b"]
        """
        if self._is_cache_valid() and OllamaModel._models_cache is not None:
            return OllamaModel._models_cache

        try:
            models = self.client.models.list()
            model_list = [m.id for m in models.data]
            self._update_cache(True, model_list)
            return model_list
        except Exception:
            return OllamaModel._models_cache or []

    @classmethod
    def refresh_cache(cls):
        """手动刷新缓存（强制下次调用时重新探测服务）

        用于 UI 中「刷新检测」按钮。
        """
        cls._last_check_time = 0
        cls._service_status_cache = None
        cls._models_cache = None

    def get_cached_status(self) -> bool:
        """获取缓存的 Ollama 服务状态

        如果缓存已过期，自动触发 is_available() 更新。
        """
        if not self._is_cache_valid() or OllamaModel._service_status_cache is None:
            self.is_available()
        return OllamaModel._service_status_cache or False