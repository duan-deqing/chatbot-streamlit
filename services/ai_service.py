"""AI服务模块"""

import openai
from typing import List, Dict
from config import AI_CONFIG


class AIService:
    """AI服务类"""
    
    @staticmethod
    def call_api(messages: List[Dict], api_key: str) -> str:
        """调用OpenAI API获取回复
        
        Args:
            messages: 消息历史列表
            api_key: API密钥
            
        Returns:
            AI回复内容
        """
        if not api_key:
            return "❌ 请先在侧边栏输入有效的 OpenAI API Key。"
        
        try:
            openai.api_key = api_key
            response = openai.ChatCompletion.create(
                model=AI_CONFIG["model"],
                messages=messages,
                temperature=AI_CONFIG["temperature"],
                max_tokens=AI_CONFIG["max_tokens"],
                top_p=AI_CONFIG["top_p"]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"⚠️ API 调用出错: {str(e)}"