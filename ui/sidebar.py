"""侧边栏UI模块"""

import streamlit as st
from data_models import ConversationManager
from models import ModelManager
from ui.sidebar_models import render_model_selector, render_ollama_manager
from ui.sidebar_history import render_history_section


def render_sidebar(conv_manager: ConversationManager, model_manager: ModelManager) -> str:
    """渲染侧边栏
    
    Args:
        conv_manager: 对话管理器
        model_manager: 模型管理器
        
    Returns:
        当前API密钥
    """
    with st.sidebar:
        st.title("🤖 AI Chat")
        
        api_key_input = st.text_input(
            "OpenAI API Key",
            type="password",
            value=st.session_state.get("api_key", ""),
            help="输入你的 OpenAI API 密钥，用于调用 GPT 模型",
            placeholder="sk-..."
        )
        if api_key_input:
            st.session_state.api_key = api_key_input
            model_manager.set_openai_api_key(api_key_input)
        
        if not st.session_state.get("api_key", ""):
            st.warning("⚠️ 使用非本地模型请在上方输入 API Key")

        # 渲染几个组件
        render_model_selector(model_manager)
        render_ollama_manager(model_manager)
        render_history_section(conv_manager)

    return st.session_state.get("api_key", "")