"""AI服务模块"""

from typing import List, Dict
from models.base import BaseModel


class AIService:
    """AI服务类"""
    
    @staticmethod
    def call_model(model: BaseModel, messages: List[Dict]) -> str:
        """调用模型获取回复
        
        Args:
            model: 模型实例
            messages: 消息历史列表
            
        Returns:
            AI回复内容
        """
        if model is None:
            return "❌ 请先选择一个模型。"
        
        if not model.is_available():
            return f"❌ 模型 {model.name} 不可用，请检查配置。"
        
        return model.chat(messages)