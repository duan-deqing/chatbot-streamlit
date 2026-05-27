"""侧边栏UI模块"""

import streamlit as st
from data import ConversationManager
from ui.sidebar_history import render_history_section


def render_sidebar(conv_manager: ConversationManager):
    """渲染侧边栏（仅保留标题和历史记录，API Key 和模型配置已移至设置弹窗）"""
    with st.sidebar:
        st.title("🤖 AI Chat")
        render_history_section(conv_manager)
        
        if st.button(
            "⚙️ 设置",
            key="settings_btn",
            use_container_width=True
        ):
            st.session_state.show_settings = True
            st.rerun()