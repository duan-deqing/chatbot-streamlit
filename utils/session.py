"""Session 状态管理模块

负责 Streamlit session_state 中所有全局状态的初始化。
每次页面刷新时由 app.py 调用，确保必要的键存在且默认值正确。
"""

import streamlit as st
from data import ConversationManager
from models import ModelManager


def init_session_state() -> tuple:
    """初始化所有必需的 session_state 变量

    幂等操作：已存在的键不会被覆盖。

    Returns:
        (ConversationManager, ModelManager) 元组，供 app.py 使用
    """
    if "conversation_manager" not in st.session_state:
        conv_manager = ConversationManager()
        conv_manager.create_conversation()
        st.session_state.conversation_manager = conv_manager

    if "model_manager" not in st.session_state:
        st.session_state.model_manager = ModelManager()

    # 当前选中模型的 key，供 chat.py 和 sidebar_models.py 共享
    if "current_model_key" not in st.session_state:
        st.session_state.current_model_key = "openai_gpt-3.5-turbo"

    # 流式输出开关
    if "enable_streaming" not in st.session_state:
        st.session_state.enable_streaming = True

    # 模型参数默认值（设置弹窗可修改）
    if "temperature" not in st.session_state:
        st.session_state.temperature = 0.7

    if "max_tokens" not in st.session_state:
        st.session_state.max_tokens = 1000

    if "top_p" not in st.session_state:
        st.session_state.top_p = 0.9

    return st.session_state.conversation_manager, st.session_state.model_manager