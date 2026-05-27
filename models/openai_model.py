"""OpenAI模型实现"""

import openai
from typing import List, Dict, Generator
from models.base import BaseModel, ModelConfig


class OpenAIModel(BaseModel):
    """OpenAI模型"""
    
    def __init__(self, config: ModelConfig, api_key: str = ""):
        super().__init__(config)
        self.api_key = api_key
        self._client = None
    
    def _get_client(self) -> openai.OpenAI:
        """获取或创建客户端"""
        if self._client is None or self._client.api_key != self.api_key:
            self._client = openai.OpenAI(api_key=self.api_key)
        return self._client
    
    def chat(self, messages: List[Dict], **kwargs) -> str:
        """调用OpenAI API
        
        Args:
            messages: 消息列表
            **kwargs: 额外参数
            
        Returns:
            模型回复
        """
        if not self.api_key:
            return "❌ 请先输入有效的 OpenAI API Key。"
        
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
        """流式调用 OpenAI API
        
        Args:
            messages: 消息列表
            **kwargs: 额外参数
            
        Yields:
            逐段模型回复内容
        """
        if not self.api_key:
            yield "❌ 请先输入有效的 OpenAI API Key。"
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
        """检查是否可用"""
        return bool(self.api_key)
    
    def set_api_key(self, api_key: str):
        """设置API密钥"""
        self.api_key = api_key