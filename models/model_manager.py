"""模型管理器"""

from typing import Dict, List, Optional
from config import OLLAMA_BASE_URL
from models.base import BaseModel, ModelConfig
from models.openai_model import OpenAIModel
from models.ollama_model import OllamaModel


# 预定义的OpenAI模型配置
OPENAI_MODELS = {
    "gpt-3.5-turbo": ModelConfig(
        name="GPT-3.5 Turbo",
        model_id="gpt-3.5-turbo",
        temperature=0.7,
        max_tokens=1000,
        top_p=0.9
    ),
    "gpt-4": ModelConfig(
        name="GPT-4",
        model_id="gpt-4",
        temperature=0.7,
        max_tokens=1000,
        top_p=0.9
    ),
    "gpt-4-turbo": ModelConfig(
        name="GPT-4 Turbo",
        model_id="gpt-4-turbo-preview",
        temperature=0.7,
        max_tokens=1000,
        top_p=0.9
    )
}

# 默认Ollama配置
DEFAULT_OLLAMA_CONFIG = ModelConfig(
    name="Ollama 本地模型",
    model_id="llama2",
    temperature=0.7,
    max_tokens=1000,
    top_p=0.9
)


class ModelManager:
    """模型管理器"""
    
    def __init__(self):
        self._models: Dict[str, BaseModel] = {}
        self._init_models()
    
    def _init_models(self):
        """初始化模型"""
        # 初始化OpenAI模型
        for model_key, config in OPENAI_MODELS.items():
            self._models[f"openai_{model_key}"] = OpenAIModel(config)
        
        # 初始化Ollama模型
        self._models["ollama_default"] = OllamaModel(DEFAULT_OLLAMA_CONFIG, OLLAMA_BASE_URL)
    
    def get_model(self, model_key: str) -> Optional[BaseModel]:
        """获取模型
        
        Args:
            model_key: 模型键名
            
        Returns:
            模型实例
        """
        return self._models.get(model_key)
    
    def get_all_models(self) -> Dict[str, BaseModel]:
        """获取所有模型"""
        return self._models
    
    def get_openai_models(self) -> Dict[str, OpenAIModel]:
        """获取所有OpenAI模型"""
        return {k: v for k, v in self._models.items() if isinstance(v, OpenAIModel)}
    
    def get_ollama_models(self) -> Dict[str, OllamaModel]:
        """获取所有Ollama模型"""
        return {k: v for k, v in self._models.items() if isinstance(v, OllamaModel)}
    
    def add_ollama_model(self, model_id: str, name: str = None) -> str:
        """添加新的Ollama模型
        
        Args:
            model_id: Ollama模型ID
            name: 显示名称
            
        Returns:
            模型键名
        """
        config = ModelConfig(
            name=name or model_id,
            model_id=model_id,
            temperature=0.7,
            max_tokens=1000,
            top_p=0.9
        )
        key = f"ollama_{model_id}"
        self._models[key] = OllamaModel(config, OLLAMA_BASE_URL)
        return key
    
    def set_openai_api_key(self, api_key: str):
        """设置所有OpenAI模型的API密钥"""
        for model in self.get_openai_models().values():
            model.set_api_key(api_key)