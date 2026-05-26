"""Ollama本地模型实现"""

import time
import httpx
import openai
from typing import List, Dict, Optional
from models.base import BaseModel, ModelConfig


class OllamaModel(BaseModel):
    """Ollama本地模型（使用OpenAI SDK）"""
    
    # 类级别缓存，所有实例共享
    _service_status_cache: Optional[bool] = None
    _models_cache: Optional[List[str]] = None
    _last_check_time: float = 0
    _cache_ttl: float = 300  # 缓存有效期（秒），默认5分钟
    
    def __init__(self, config: ModelConfig, base_url: str = "http://localhost:11434/v1"):
        super().__init__(config)
        self.base_url = base_url.rstrip('/')
        self.client = openai.OpenAI(
            base_url=self.base_url,
            api_key="ollama"  # Ollama不需要真实的API key
        )
    
    def chat(self, messages: List[Dict], **kwargs) -> str:
        """调用Ollama API（使用OpenAI SDK）
        
        Args:
            messages: 消息列表
            **kwargs: 额外参数
            
        Returns:
            模型回复
        """
        try:
            response = self.client.chat.completions.create(
                model=self.config.model_id,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                top_p=self.config.top_p
            )
            return response.choices[0].message.content
        except (httpx.ConnectError, httpx.ConnectTimeout):
            return "❌ 无法连接到 Ollama 服务，请确保 Ollama 已启动。"
        except Exception as e:
            return f"⚠️ Ollama 调用出错: {str(e)}"
    
    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        return (time.time() - OllamaModel._last_check_time) < OllamaModel._cache_ttl
    
    def _update_cache(self, status: bool, models: List[str]):
        """更新缓存"""
        OllamaModel._service_status_cache = status
        OllamaModel._models_cache = models
        OllamaModel._last_check_time = time.time()
    
    def is_available(self) -> bool:
        """检查Ollama服务是否可用（带缓存）"""
        if self._is_cache_valid() and OllamaModel._service_status_cache is not None:
            return OllamaModel._service_status_cache
        
        try:
            models = self.client.models.list()
            status = True
            model_list = [m.id for m in models.data]
            self._update_cache(status, model_list)
            return status
        except:
            self._update_cache(False, [])
            return False
    
    def list_models(self) -> List[str]:
        """获取本地可用的模型列表（带缓存）"""
        if self._is_cache_valid() and OllamaModel._models_cache is not None:
            return OllamaModel._models_cache
        
        try:
            models = self.client.models.list()
            model_list = [m.id for m in models.data]
            self._update_cache(True, model_list)
            return model_list
        except:
            return OllamaModel._models_cache or []
    
    @classmethod
    def refresh_cache(cls):
        """手动刷新缓存"""
        cls._last_check_time = 0
        cls._service_status_cache = None
        cls._models_cache = None
    
    def get_cached_status(self) -> bool:
        """获取缓存的服务状态，如果缓存无效则更新"""
        if not self._is_cache_valid() or OllamaModel._service_status_cache is None:
            self.is_available()
        return OllamaModel._service_status_cache or False