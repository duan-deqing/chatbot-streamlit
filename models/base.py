"""模型基类

定义所有 AI 模型必须遵循的抽象接口，以及通用的配置数据类。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Generator
from dataclasses import dataclass


@dataclass
class ModelConfig:
    """模型配置数据类

    统一承载内置模型、自定义模型、Ollama 模型的所有配置字段。
    内置模型 is_builtin=True，自定义模型 is_builtin=False。
    """
    name: str                        # 显示名称，如 "GPT-4 Turbo"
    model_id: str                    # API 调用时的模型标识，如 "gpt-4-turbo-preview"
    provider: str = ""               # 供应商标识，如 "openai", "ollama", "DeepSeek"
    base_url: str = ""               # API 端点地址，Ollama 默认为 http://localhost:11434/v1
    api_key: str = ""                # 模型级 API Key（自定义模型存储在此，OpenAI 由供应商级管理）
    is_builtin: bool = False         # True=系统内置模型，False=用户自定义模型
    temperature: float = 0.7         # 创造性参数（0~2）
    max_tokens: int = 1000           # 最大输出 token 数
    top_p: float = 0.9               # 核采样阈值


class BaseModel(ABC):
    """模型抽象基类

    所有模型实现（OpenAIModel、OllamaModel 等）必须继承此类并实现三个抽象方法：
    - chat(): 同步对话
    - chat_stream(): 流式对话
    - is_available(): 可用性检查
    """

    def __init__(self, config: ModelConfig):
        self.config = config

    @abstractmethod
    def chat(self, messages: List[Dict], **kwargs) -> str:
        """同步聊天

        Args:
            messages: OpenAI 格式消息列表 [{"role": "user", "content": "..."}]
            **kwargs: 可覆盖 temperature, max_tokens, top_p 等参数

        Returns:
            模型回复文本
        """
        pass

    def chat_stream(self, messages: List[Dict], **kwargs) -> Generator[str, None, None]:
        """流式聊天（默认降级为同步一次性输出）

        子类可覆盖为真正的 SSE 流式实现。
        """
        result = self.chat(messages, **kwargs)
        yield result

    @abstractmethod
    def is_available(self) -> bool:
        """检查模型是否可用

        对于 OpenAI：检查 API Key 是否已配置
        对于 Ollama：检查本地服务是否可连接
        """
        pass

    @property
    def name(self) -> str:
        """获取模型显示名称"""
        return self.config.name