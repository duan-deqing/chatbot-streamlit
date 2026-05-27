"""OpenAI 模型实现

基于 OpenAI Python SDK 的聊天模型，同时兼容所有 OpenAI API 格式的第三方服务
（如 DeepSeek、Groq、智谱等），通过 ModelConfig.base_url 指定自定义端点。
"""

import openai
from typing import List, Dict, Generator
from models.base import BaseModel, ModelConfig


class OpenAIModel(BaseModel):
    """OpenAI 兼容模型

    同时服务于：
    - 内置 OpenAI 模型（通过 provider="openai" + 供应商级 API Key）
    - 自定义第三方模型（通过 provider="自定义" + 模型级 API Key + 自定义 base_url）

    API Key 来源优先级：
    1. 实例化时传入的 api_key 参数
    2. ModelConfig.api_key（自定义模型存储位置）
    3. ModelManager.set_openai_api_key() 注入（供应商级 Key，仅 OpenAI 使用）
    """

    def __init__(self, config: ModelConfig, api_key: str = ""):
        super().__init__(config)
        self.api_key = api_key or config.api_key
        self.base_url = config.base_url or None
        self._client = None

    def _get_client(self) -> openai.OpenAI:
        """延迟创建 OpenAI 客户端（API Key 变更时自动重建）"""
        kwargs = {"api_key": self.api_key}
        if self.base_url:
            kwargs["base_url"] = self.base_url
        if self._client is None or self._client.api_key != self.api_key:
            self._client = openai.OpenAI(**kwargs)
        return self._client

    def chat(self, messages: List[Dict], **kwargs) -> str:
        """同步聊天

        Args:
            messages: OpenAI 格式消息列表
            **kwargs: temperature, max_tokens, top_p 可覆盖默认值

        Returns:
            模型回复内容，错误时返回带前缀的错误提示
        """
        if not self.api_key:
            return "❌ 请先为当前模型配置 API Key。"

        try:
            temperature = kwargs.get("temperature", self.config.temperature)
            max_tokens = kwargs.get("max_tokens", self.config.max_tokens)
            top_p = kwargs.get("top_p", self.config.top_p)
            client = self._get_client()
            response = client.chat.completions.create(
                model=self.config.model_id,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"⚠️ API 调用出错: {type(e).__name__}"

    def chat_stream(self, messages: List[Dict], **kwargs) -> Generator[str, None, None]:
        """流式聊天（SSE 逐 token 输出）

        Args:
            messages: OpenAI 格式消息列表
            **kwargs: temperature, max_tokens, top_p 可覆盖默认值

        Yields:
            逐段模型回复文本
        """
        if not self.api_key:
            yield "❌ 请先为当前模型配置 API Key。"
            return

        try:
            temperature = kwargs.get("temperature", self.config.temperature)
            max_tokens = kwargs.get("max_tokens", self.config.max_tokens)
            top_p = kwargs.get("top_p", self.config.top_p)
            client = self._get_client()
            stream = client.chat.completions.create(
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
        except Exception as e:
            yield f"⚠️ API 调用出错: {type(e).__name__}"

    def is_available(self) -> bool:
        """检查是否有 API Key 配置"""
        return bool(self.api_key)

    def set_api_key(self, api_key: str):
        """设置 API Key 并重置客户端（下次调用时重新创建）"""
        self.api_key = api_key
        self._client = None