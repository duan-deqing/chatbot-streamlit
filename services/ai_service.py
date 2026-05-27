"""AI服务模块"""

from typing import List, Dict, Generator
from models.base import BaseModel


class AIService:
    """AI服务类"""
    
    @staticmethod
    def call_model(model: BaseModel, messages: List[Dict], **params) -> str:
        """调用模型获取回复
        
        Args:
            model: 模型实例
            messages: 消息历史列表
            **params: 模型参数覆盖（temperature, max_tokens, top_p）
            
        Returns:
            AI回复内容
        """
        if model is None:
            return "❌ 请先选择一个模型。"
        
        if not model.is_available():
            return f"❌ 模型 {model.name} 不可用，请检查配置。"
        
        return model.chat(messages, **params)
    
    @staticmethod
    def call_model_stream(model: BaseModel, messages: List[Dict], **params) -> Generator[str, None, None]:
        """流式调用模型获取回复
        
        Args:
            model: 模型实例
            messages: 消息历史列表
            **params: 模型参数覆盖（temperature, max_tokens, top_p）
            
        Yields:
            逐段 AI 回复内容
        """
        if model is None:
            yield "❌ 请先选择一个模型。"
            return
        
        if not model.is_available():
            yield f"❌ 模型 {model.name} 不可用，请检查配置。"
            return
        
        yield from model.chat_stream(messages, **params)