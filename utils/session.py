"""Session管理工具模块"""

import streamlit as st
from data_models import ConversationManager
from models import ModelManager


def init_session_state() -> tuple:
    """初始化所有必需的session state变量
    
    Returns:
        (对话管理器, 模型管理器) 元组
    """
    if "conversation_manager" not in st.session_state:
        conv_manager = ConversationManager()
        conv_manager.create_conversation()
        st.session_state.conversation_manager = conv_manager
    
    if "model_manager" not in st.session_state:
        st.session_state.model_manager = ModelManager()
    
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""
    
    if "current_model_key" not in st.session_state:
        st.session_state.current_model_key = "openai_gpt-3.5-turbo"
    
    return st.session_state.conversation_manager, st.session_state.model_manager