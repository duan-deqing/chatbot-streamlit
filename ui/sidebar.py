"""侧边栏 UI 模块

负责渲染 Streamlit 侧边栏的整体布局：
- 应用标题
- 对话历史记录
- 设置入口按钮
"""

import uuid
import streamlit as st
from data import ConversationManager
from ui.sidebar_history import render_history_section


def render_sidebar(conv_manager: ConversationManager):
    """渲染侧边栏

    包含：
    1. 应用标题（🤖 AI Chat）
    2. 新建对话 + 历史记录列表（委托 sidebar_history.py）
    3. ⚙️ 设置按钮（生成唯一 session token 并打开设置弹窗）

    Args:
        conv_manager: 对话管理器
    """
    with st.sidebar:
        st.title("🤖 AI Chat")
        render_history_section(conv_manager)

        if st.button(
            "⚙️ 设置",
            key="settings_btn",
            use_container_width=True
        ):
            st.session_state.show_settings = True
            # 生成唯一 session token，用于防止 X 关闭后意外重新弹出
            st.session_state._settings_session = uuid.uuid4().hex
            st.rerun()