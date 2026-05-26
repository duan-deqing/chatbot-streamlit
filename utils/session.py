"""Session管理工具模块"""

import streamlit as st
from models import ConversationManager


def init_session_state() -> ConversationManager:
    """初始化所有必需的session state变量
    
    Returns:
        对话管理器实例
    """
    if "conversation_manager" not in st.session_state:
        conv_manager = ConversationManager()
        conv_manager.create_conversation()
        st.session_state.conversation_manager = conv_manager
    
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""
    
    return st.session_state.conversation_manager