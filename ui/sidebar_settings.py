"""设置弹窗模块

使用 Streamlit 原生 st.dialog 实现设置弹窗，按功能区分为标签页。
状态管理：sidebar 中设置按钮将 show_settings 置为 True，
render_settings() 检测到 True 时弹出对话框，渲染完成后立即复位为 False，
避免下一次 rerun（如点击对话卡片）时重复弹出。
"""

import streamlit as st
from ui.sidebar_models import render_model_selector, render_ollama_manager


@st.dialog("设置", width="large")
def settings_dialog(model_manager):
    """设置弹窗
    
    Args:
        model_manager: 模型管理器实例
    """
    st.markdown("""
    <style>
    [data-testid="stDialog"] > div > div {
        width: 65vw !important;
        max-width: 80vw !important;
    }
    </style>
    """, unsafe_allow_html=True)

    tab_api, tab_model = st.tabs(["API Key", "模型配置"])

    with tab_api:
        st.markdown("### OpenAI API Key 配置")
        st.caption("API Key 仅存储在本地会话中，不会上传到任何服务器。")

        col1, col2 = st.columns([3, 1])
        with col1:
            api_key_input = st.text_input(
                "API Key",
                type="password",
                value=st.session_state.get("api_key", ""),
                placeholder="sk-...",
                label_visibility="collapsed"
            )
        with col2:
            if st.button("保存", key="save_api_key", use_container_width=True):
                if api_key_input:
                    st.session_state.api_key = api_key_input
                    model_manager.set_openai_api_key(api_key_input)
                    st.success("已保存")
                else:
                    st.warning("请输入 Key")

        if st.session_state.get("api_key", ""):
            masked = st.session_state.api_key[:8] + "****" + st.session_state.api_key[-4:]
            st.success(f"已配置: `{masked}`")
        else:
            st.warning("⚠️ 未配置 API Key，无法使用 OpenAI 系列模型。")

    with tab_model:
        render_model_selector(model_manager)
        st.divider()
        render_ollama_manager(model_manager)

    st.divider()
    _, col_close, _ = st.columns([2, 1, 2])
    with col_close:
        if st.button("关闭", key="close_settings", use_container_width=True):
            st.session_state.show_settings = False
            st.rerun()


def render_settings(model_manager):
    """渲染设置弹窗入口
    
    由 app.py 在每次 rerun 时调用。
    仅在 show_settings 为 True 时弹出 st.dialog，
    并立即复位 show_settings，防止状态泄漏导致重复弹出。
    
    Args:
        model_manager: 模型管理器实例
    """
    if st.session_state.get("show_settings", False):
        settings_dialog(model_manager)
        st.session_state.show_settings = False