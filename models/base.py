"""模型基类"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class ModelConfig:
    """模型配置"""
    name: str
    model_id: str
    temperature: float = 0.7
    max_tokens: int = 1000
    top_p: float = 0.9


class BaseModel(ABC):
    """模型基类"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
    
    @abstractmethod
    def chat(self, messages: List[Dict], **kwargs) -> str:
        """发送聊天请求
        
        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            **kwargs: 额外参数
            
        Returns:
            模型回复内容
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查模型是否可用
        
        Returns:
            是否可用
        """
        pass
    
    @property
    def name(self) -> str:
        """获取模型名称"""
        return self.config.name